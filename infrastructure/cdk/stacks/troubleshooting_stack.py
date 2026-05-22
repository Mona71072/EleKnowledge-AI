from aws_cdk import (
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_logs as logs,
    aws_apigateway as apigw,
    core
)

class TroubleshootingStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, environment: str = "development", **kwargs):
        super().__init__(scope, id, **kwargs)

        self.environment = environment
        lambda_role = self._create_lambda_role()
        sites_table = self._create_sites_table()
        sessions_table = self._create_sessions_table()

        sessions_table.grant_write_data(lambda_role)  # orchestrator + kb-search1/3
        sessions_table.grant_read_data(lambda_role)   # orchestrator + history

        self.orchestrator_fn = self._create_orchestrator_lambda(lambda_role, sites_table, sessions_table)
        self.db_search_fn = self._create_db_search_lambda(lambda_role, sites_table)
        self.kb_search1_fn = self._create_kb_search1_lambda(lambda_role, sessions_table)
        self.kb_search2_fn = self._create_kb_search2_lambda(lambda_role)
        self.kb_search3_fn = self._create_kb_search3_lambda(lambda_role, sessions_table)
        self.history_fn = self._create_history_lambda(lambda_role, sessions_table)
        self.authorizer_fn = self._create_authorizer_lambda()

        self._create_api()

    def _create_lambda_role(self) -> iam.Role:
        role = iam.Role(
            self, "TroubleshootingLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="troubleshooting-lambda-role"
        )

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AWSXRayDaemonWriteAccess"))

        role.add_to_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeAgent", "bedrock-agent-runtime:InvokeAgent", "bedrock:Retrieve", "bedrock-agent-runtime:Retrieve"],
            resources=["*"]
        ))

        role.add_to_policy(iam.PolicyStatement(
            actions=["s3:GetObject", "s3:ListBucket"],
            resources=[
                "arn:aws:s3:::eleknowledge-ai-development-documents",
                "arn:aws:s3:::eleknowledge-ai-development-documents/*",
            ]
        ))

        return role

    def _create_sites_table(self) -> dynamodb.Table:
        return dynamodb.Table(
            self, "SitesTable",
            table_name="sites",
            partition_key=dynamodb.Attribute(name="constructionNumber", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

    def _create_sessions_table(self) -> dynamodb.Table:
        table = dynamodb.Table(
            self, "TroubleshootingSessionsTable",
            table_name="troubleshooting-sessions",
            partition_key=dynamodb.Attribute(name="session_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute="ttl",
        )
        table.add_global_secondary_index(
            index_name="userId-timestamp-index",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL,
        )
        return table

    def _create_orchestrator_lambda(self, role: iam.Role, sites_table: dynamodb.Table, sessions_table: dynamodb.Table) -> lambda_.Function:
        sites_table.grant_read_data(role)
        return lambda_.Function(
            self, "OrchestratorFunction",
            function_name="troubleshooting-orchestrator",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda/troubleshooting/orchestrator"),
            handler="app.lambda_handler",
            role=role,
            timeout=core.Duration.seconds(60),
            memory_size=512,
            environment={
                "AGENT_ID": "PLACEHOLDER",
                "AGENT_ALIAS_ID": "PLACEHOLDER",
                "SITES_TABLE": sites_table.table_name,
                "SESSIONS_TABLE": sessions_table.table_name,
            },
            tracing=lambda_.Tracing.ACTIVE
        )

    def _create_db_search_lambda(self, role: iam.Role, sites_table: dynamodb.Table) -> lambda_.Function:
        sites_table.grant_read_data(role)
        return lambda_.Function(
            self, "DBSearchFunction",
            function_name="troubleshooting-db-search",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda/troubleshooting/db-search"),
            handler="app.lambda_handler",
            role=role,
            timeout=core.Duration.seconds(60),
            memory_size=512,
            environment={"SITES_TABLE": sites_table.table_name},
            tracing=lambda_.Tracing.ACTIVE
        )

    def _create_kb_search1_lambda(self, role: iam.Role, sessions_table: dynamodb.Table) -> lambda_.Function:
        return lambda_.Function(
            self, "KBSearch1Function",
            function_name="troubleshooting-kb-search1",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda/troubleshooting/kb-search1"),
            handler="app.lambda_handler",
            role=role,
            timeout=core.Duration.seconds(60),
            memory_size=512,
            environment={
                "KnowledgeBaseId": "PLACEHOLDER",
                "SESSIONS_TABLE": sessions_table.table_name,
            },
            tracing=lambda_.Tracing.ACTIVE
        )

    def _create_kb_search2_lambda(self, role: iam.Role) -> lambda_.Function:
        return lambda_.Function(
            self, "KBSearch2Function",
            function_name="troubleshooting-kb-search2",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda/troubleshooting/kb-search2"),
            handler="app.lambda_handler",
            role=role,
            timeout=core.Duration.seconds(60),
            memory_size=512,
            environment={"KnowledgeBaseId": "PLACEHOLDER"},
            tracing=lambda_.Tracing.ACTIVE
        )

    def _create_kb_search3_lambda(self, role: iam.Role, sessions_table: dynamodb.Table) -> lambda_.Function:
        return lambda_.Function(
            self, "KBSearch3Function",
            function_name="troubleshooting-kb-search3",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda/troubleshooting/kb-search3"),
            handler="app.lambda_handler",
            role=role,
            timeout=core.Duration.seconds(60),
            memory_size=512,
            environment={
                "KnowledgeBaseId": "PLACEHOLDER",
                "SESSIONS_TABLE": sessions_table.table_name,
            },
            tracing=lambda_.Tracing.ACTIVE
        )

    def _create_history_lambda(self, role: iam.Role, sessions_table: dynamodb.Table) -> lambda_.Function:
        return lambda_.Function(
            self, "HistoryFunction",
            function_name="troubleshooting-history",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda/troubleshooting/history"),
            handler="app.lambda_handler",
            role=role,
            timeout=core.Duration.seconds(10),
            memory_size=256,
            environment={"SESSIONS_TABLE": sessions_table.table_name},
            tracing=lambda_.Tracing.ACTIVE
        )

    def _create_authorizer_lambda(self) -> lambda_.Function:
        # authorizer は独立ロール（Lambda基本実行権限のみ）
        authorizer_role = iam.Role(
            self, "AuthorizerRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        authorizer_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )
        return lambda_.Function(
            self, "AuthorizerFunction",
            function_name="troubleshooting-authorizer",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda/troubleshooting/authorizer"),
            handler="app.lambda_handler",
            role=authorizer_role,
            timeout=core.Duration.seconds(10),
            memory_size=256,
            environment={
                "COGNITO_REGION": self.region,
                "USER_POOL_ID": "PLACEHOLDER",
                "APP_CLIENT_ID": "PLACEHOLDER",
            },
        )

    def _create_api(self):
        token_authorizer = apigw.TokenAuthorizer(
            self, "TroubleshootingTokenAuthorizer",
            handler=self.authorizer_fn,
            results_cache_ttl=core.Duration.minutes(5),
        )

        api = apigw.RestApi(
            self, "TroubleshootingApi",
            rest_api_name="troubleshooting-api",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=["GET", "POST", "OPTIONS"],
                allow_headers=["Content-Type", "Authorization"],
            ),
        )

        analyze = api.root.add_resource("analyze")
        analyze.add_method(
            "POST",
            apigw.LambdaIntegration(self.orchestrator_fn),
            authorizer=token_authorizer,
        )

        history = api.root.add_resource("history")
        history.add_method(
            "GET",
            apigw.LambdaIntegration(self.history_fn),
            authorizer=token_authorizer,
        )
