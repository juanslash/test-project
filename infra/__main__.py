"""A DigitalOcean Python Pulumi program"""

import pulumi
import pulumi_digitalocean as digitalocean

# Our stack-specific configuration.
config = pulumi.Config()
repo = config.require("repo")
branch = config.require("branch")

# The DigitalOcean region to deploy into.
region = digitalocean.Region.SFO3

# Our postgreSQL cluster (currently just one node).
cluster = digitalocean.DatabaseCluster("postgres-test", digitalocean.DatabaseClusterArgs(
    engine="pg",
    version="15",
    region=region,
    size="db-s-1vcpu-1gb",
    node_count=1
))

# The database
psql = digitalocean.DatabaseDb(
    "database",
    cluster_id=cluster.id
)

# The App Platform specs.
app = digitalocean.App("app", digitalocean.AppArgs(
    spec=digitalocean.AppSpecArgs(
        name="modelw-sample",
        region=region,
        ingress=digitalocean.AppSpecIngressArgs(
            rules=[
                digitalocean.AppSpecIngressRuleArgs(
                    component=digitalocean.AppSpecIngressRuleComponentArgs(
                        name="front",
                        preserve_path_prefix=True
                    ),
                    match=digitalocean.AppSpecIngressRuleMatchArgs(
                        path=digitalocean.AppSpecIngressRuleMatchPathArgs(
                            prefix="/"
                        ),
                    )
                ),
                digitalocean.AppSpecIngressRuleArgs(
                    component=digitalocean.AppSpecIngressRuleComponentArgs(
                        name="api",
                        preserve_path_prefix=True
                    ),
                    match=digitalocean.AppSpecIngressRuleMatchArgs(
                        path=digitalocean.AppSpecIngressRuleMatchPathArgs(
                            prefix="/__private__",
                        ),
                    )
                )
            ]
        ),
        services=[
            # The Nuxt frontend.
            digitalocean.AppSpecServiceArgs(
                name="front",
                dockerfile_path="/front/Dockerfile",
                github=digitalocean.AppSpecServiceGithubArgs(
                    repo=repo,
                    branch=branch,
                ),
                source_dir="/front",
                http_port=3000,
                instance_size_slug="basic-xxs",
                instance_count=1,
                envs=[
                    digitalocean.AppSpecServiceEnvArgs(
                        key="BASE_URL",
                        scope="RUN_AND_BUILD_TIME",
                        value=pulumi.Output.concat("${APP_URL}"),
                        type="GENERAL"
                    ),
                    digitalocean.AppSpecServiceEnvArgs(
                        key="NUXT_API_URL",
                        scope="RUN_AND_BUILD_TIME",
                        value="${api.PRIVATE_URL}",
                        type="GENERAL"
                    ),
                    digitalocean.AppSpecServiceEnvArgs(
                        key="NUXT_PROXY_OPTIONS_TARGET",
                        scope="RUN_AND_BUILD_TIME",
                        value="${api.PRIVATE_URL}",
                        type="GENERAL"
                    ),
                ],
                run_command=None,
            ),
            # The Django backend.
            digitalocean.AppSpecServiceArgs(
                name="api",
                dockerfile_path="/api/Dockerfile",
                github=digitalocean.AppSpecServiceGithubArgs(
                    repo=repo,
                    branch=branch,
                ),
                source_dir="/api",
                http_port=8000,
                instance_size_slug="basic-xxs",
                instance_count=1,
                # To connect to PostgreSQL, the service needs a DATABASE_URL, which
                # is conveniently exposed as an environment variable because the
                # database belongs to the app (see below).
                envs=[
                    digitalocean.AppSpecServiceEnvArgs(
                        key="SECRET_KEY",
                        scope="RUN_AND_BUILD_TIME",
                        value="kTOp03ZRCTs4pgD1qrmj5Te84weshVw6MjOTRPubXFB4kSfbqzrdR2",
                        type="SECRET"
                    ),
                    digitalocean.AppSpecServiceEnvArgs(
                        key="ENVIRONMENT",
                        scope="RUN_AND_BUILD_TIME",
                        value="develop",
                        type="GENERAL"
                    ),
                    digitalocean.AppSpecServiceEnvArgs(
                        key="DATABASE_URL",
                        scope="RUN_AND_BUILD_TIME",
                        value="${psql.DATABASE_URL}",
                        type="GENERAL"
                    ),
                    digitalocean.AppSpecServiceEnvArgs(
                        key="BASE_URL",
                        scope="RUN_AND_BUILD_TIME",
                        value="${APP_URL}",
                        type="GENERAL"
                    )
                ],
                run_command=None,
            )
        ],

        # Include the PostgreSQL cluster as an integrated App Platform component.
        databases=[
            digitalocean.AppSpecDatabaseArgs(
                # The `db` name defines the prefix of the tokens used (above) to
                # read the environment variables exposed by the database cluster.
                name="psql",
                production=True,
                # A reference to the managed cluster we declared above.
                cluster_name=cluster.name,
                # The engine value must be uppercase, so we transform it with Python.
                engine=cluster.engine.apply(lambda engine: engine.upper())
            )
        ],

        # jobs=[
        #     digitalocean.AppSpecJobArgs(
        #         name="migrate",
        #         envs=[
        #             digitalocean.AppSpecServiceEnvArgs(
        #                 key="SECRET_KEY",
        #                 scope="RUN_AND_BUILD_TIME",
        #                 value="kTOp03ZRCTs4pgD1qrmj5Te84weshVw6MjOTRPubXFB4kSfbqzrdR2",
        #                 type="SECRET"
        #             ),
        #             digitalocean.AppSpecServiceEnvArgs(
        #                 key="ENVIRONMENT",
        #                 scope="RUN_AND_BUILD_TIME",
        #                 value="develop",
        #                 type="GENERAL"
        #             ),
        #             digitalocean.AppSpecServiceEnvArgs(
        #                 key="DATABASE_URL",
        #                 scope="RUN_AND_BUILD_TIME",
        #                 value="${psql.DATABASE_URL}",
        #                 type="GENERAL"
        #             ),
        #             digitalocean.AppSpecServiceEnvArgs(
        #                 key="BASE_URL",
        #                 scope="RUN_AND_BUILD_TIME",
        #                 value="${APP_URL}",
        #                 type="GENERAL"
        #             ),
        #         ],
        #         dockerfile_path="/api/Dockerfile",
        #         git=digitalocean.AppSpecServiceGitArgs(
        #             repo_clone_url=repo,
        #             branch=branch,
        #         ),
        #         run_command="modelw-docker run python manage.py migrate",
        #         source_dir="/api",
        #         instance_count=1,
        #         instance_size_slug="basic-xxs",
        #         kind="PRE_DEPLOY"
        #     )
        # ]
    ),
))

playground = digitalocean.Project(
    "test-app",
    description="A project to represent development resources.",
    purpose="Web Application",
    environment="Development",
    resources=[app.app_urn]
)

# The DigitalOcean-assigned URL for our app.
pulumi.export("liveUrl", app.live_url)
