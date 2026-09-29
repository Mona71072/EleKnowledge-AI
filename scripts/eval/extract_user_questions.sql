-- Athena positional execution parameters: weeks_back, max_rows.
-- Example values are supplied by the operator at query execution time; do not
-- commit extracted results. Internal keys are used for grouping/sequencing only
-- and never appear in the final projection.
WITH window_start AS (
    SELECT date_add('week', -CAST(? AS integer), current_date) AS start_date
),
extraction_window AS (
    SELECT
        date_format(start_date, '%Y-%m-%d') AS start_dt,
        -- chat-archive decides dt from the first record of each batch, so a batch
        -- crossing midnight can store later events under the previous day.
        date_format(date_add('day', -1, start_date), '%Y-%m-%d') AS remove_start_dt
    FROM window_start
),
latest_events AS (
    SELECT
        dt,
        approximatecreationdatetime,
        eventid,
        eventname,
        newimage,
        oldimage,
        coalesce(newimage.sessionid, oldimage.sessionid) AS session_key,
        coalesce(newimage.messageid, oldimage.messageid) AS message_key,
        row_number() OVER (
            PARTITION BY coalesce(newimage.sessionid, oldimage.sessionid),
                         coalesce(newimage.messageid, oldimage.messageid)
            ORDER BY approximatecreationdatetime DESC, eventid DESC
        ) AS revision_rank
    FROM chatlogs_archive
    CROSS JOIN extraction_window
    WHERE dt >= extraction_window.start_dt
      -- TTL REMOVE records must not replace the last message image.
      AND (eventname <> 'REMOVE'
           OR coalesce(useridentity.principalid, '') <> 'dynamodb.amazonaws.com')
      AND coalesce(newimage.sessionid, oldimage.sessionid) IS NOT NULL
      AND coalesce(newimage.messageid, oldimage.messageid) IS NOT NULL
),
removed_messages AS (
    -- Message deletion follows creation, so no upper bound is needed. Ignore
    -- DynamoDB TTL removals; chat-archive preserves userIdentity in the archive.
    SELECT DISTINCT
        coalesce(newimage.sessionid, oldimage.sessionid) AS session_key,
        coalesce(newimage.messageid, oldimage.messageid) AS message_key
    FROM chatlogs_archive
    CROSS JOIN extraction_window
    WHERE eventname = 'REMOVE'
      AND dt >= extraction_window.remove_start_dt
      AND coalesce(useridentity.principalid, '') <> 'dynamodb.amazonaws.com'
),
feedback_at_latest_time AS (
    SELECT
        events.session_key,
        events.message_key,
        count(DISTINCT events.newimage.feedback) AS feedback_value_count,
        count_if(events.newimage.feedback IS NULL) AS null_feedback_count
    FROM latest_events AS events
    JOIN (
        SELECT session_key, message_key, max(approximatecreationdatetime) AS latest_time
        FROM latest_events
        GROUP BY session_key, message_key
    ) AS latest_time
      ON events.session_key = latest_time.session_key
     AND events.message_key = latest_time.message_key
     AND events.approximatecreationdatetime = latest_time.latest_time
    WHERE events.newimage.role = 'assistant'
    GROUP BY events.session_key, events.message_key
),
messages AS (
    SELECT
        latest_events.session_key AS internal_session_key,
        latest_events.message_key AS internal_message_key,
        newimage.timestamp AS message_timestamp,
        newimage.role AS role,
        newimage.content AS content,
        newimage.deleted AS deleted,
        newimage.responsetype AS response_type,
        CASE WHEN feedback_at_latest_time.feedback_value_count > 1
                    OR (feedback_at_latest_time.feedback_value_count > 0
                        AND feedback_at_latest_time.null_feedback_count > 0)
             THEN NULL
             ELSE newimage.feedback END AS feedback,
        newimage.feedbackreason AS feedback_reason,
        newimage.queryfilters.modeltype AS model_type
    FROM latest_events
    LEFT JOIN feedback_at_latest_time
      ON latest_events.session_key = feedback_at_latest_time.session_key
     AND latest_events.message_key = feedback_at_latest_time.message_key
    LEFT JOIN removed_messages
      ON latest_events.session_key = removed_messages.session_key
     AND latest_events.message_key = removed_messages.message_key
    WHERE revision_rank = 1
      AND eventname <> 'REMOVE'
      AND removed_messages.session_key IS NULL
      AND newimage.role IN ('user', 'assistant')
      AND coalesce(newimage.deleted, false) = false
),
sequenced AS (
    SELECT
        *,
        lead(role) OVER session_order AS next_role,
        lead(response_type) OVER session_order AS next_response_type,
        lead(feedback) OVER session_order AS next_feedback,
        lead(feedback_reason) OVER session_order AS next_feedback_reason,
        lead(model_type) OVER session_order AS next_model_type,
        lag(role) OVER session_order AS previous_role,
        lag(response_type) OVER session_order AS previous_response_type,
        lag(content, 1) OVER session_order AS previous_content,
        lag(content, 2) OVER session_order AS two_messages_back_content,
        lag(role, 2) OVER session_order AS two_messages_back_role
    FROM messages
    WINDOW session_order AS (
        PARTITION BY internal_session_key
        ORDER BY message_timestamp, internal_message_key
    )
),
eligible_questions AS (
    SELECT
        *,
        row_number() OVER (
            ORDER BY message_timestamp DESC, internal_session_key, internal_message_key
        ) AS extract_rank
    FROM sequenced
    WHERE role = 'user'
      AND next_role = 'assistant'
),
limited_questions AS (
    SELECT *
    FROM eligible_questions
    WHERE extract_rank <= CAST(? AS bigint)
)
SELECT
    content AS question,
    next_response_type AS response_type,
    next_feedback AS feedback,
    next_feedback_reason AS feedback_reason,
    next_model_type AS model_type,
    CASE WHEN previous_role = 'assistant' AND previous_response_type = 'clarify'
                  AND two_messages_back_role = 'user'
        THEN two_messages_back_content END AS previous_user_question,
    CASE WHEN previous_role = 'assistant' AND previous_response_type = 'clarify'
        THEN previous_content END AS previous_assistant_content,
    (previous_role = 'assistant' AND previous_response_type = 'clarify')
        AS preceded_by_clarify,
    CAST(NULL AS boolean) AS document_opened
FROM limited_questions
ORDER BY extract_rank;
