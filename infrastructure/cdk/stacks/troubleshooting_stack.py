from aws_cdk import (
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_logs as logs,
    core
)

class TroubleshootingStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, environment: str = "development", **kwargs):
        super().__init__(scope, id, **kwargs)
        
        self.environment = environment
        lambda_role = self._create_lambda_role()
        sites_table = self._create_sites_table()
        
        self.orchestrator_fn = self._create_orchestrator_lambda(lambda_role, sites_table)
        self.db_search_fn = self._create_db_search_lambda(lambda_role, sites_table)
        self.kb_search1_fn = self._create_kb_search1_lambda(lambda_role)
        self.kb_search2_fn = self._create_kb_search2_lambda(lambda_role)
        self.kb_search3_fn = self._create_kb_search3_lambda(lambda_role)
    
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
        
        return role
    
    def _create_sites_table(self) -> dynamodb.Table:
        return dynamodb.Table(
            self, "SitesTable",
            table_name="sites",
            partition_key=dynamodb.Attribute(name="constructionNumber", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
    
    def _create_orchestrator_lambda(self, role: iam.Role, sites_table: dynamodb.Table) -> lambda_.Function:
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
            environment={"AGENT_ID": "PLACEHOLDER", "AGENT_ALIAS_ID": "PLACEHOLDER", "SITES_TABLE": sites_table.table_name},
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
    
    def _create_kb_search1_lambda(self, role: iam.Role) -> lambda_.Function:
        return lambda_.Function(
            self, "KBSearch1Function",
            function_name="troubleshooting-kb-search1",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda/troubleshooting/kb-search1"),
            handler="app.lambda_handler",
            role=role,
            timeout=core.Duration.seconds(60),
            memory_size=512,
            environment={"KB_ID": "PLACEHOLDER"},
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
            environment={"KB_ID": "PLACEHOLDER"},
            tracing=lambda_.Tracing.ACTIVE
        )
    
    def _create_kb_search3_lambda(self, role: iam.Role) -> lambda_.Function:
        return lambda_.Function(
            self, "KBSearch3Function",
            function_name="troubleshooting-kb-search3",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda/troubleshooting/kb-search3"),
            handler="app.lambda_handler",
            role=role,
            timeout=core.Duration.seconds(60),
            memory_size=512,
            environment={"KB_ID": "PLACEHOLDER"},
            tracing=lambda_.Tracing.ACTIVE
        )