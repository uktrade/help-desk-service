# Environment Variables

| Environment variable       | Default | Notes                                                                                    |
|----------------------------|---------|------------------------------------------------------------------------------------------|
| APP_ENV                    | None    | Used by PaaS instance to know what env is running                                        |
| DEBUG                      | false   |                                                                                          |
| DJANGO_SETTINGS_MODULE     | false   |                                                                                          |
| DATABASE_URL               | false   |                                                                                          |
| SECRET_KEY                 | None    |                                                                                          |
| ALLOWED_HOSTS              | None    |                                                                                          |
| CSRF_TRUSTED_ORIGINS       | None    |                                                                                          |
| SET_HSTS_HEADERS           | None    |                                                                                          |
| REDIS_URL                  | None    |                                                                                          |
| ELASTIC_APM_SERVER_TIMEOUT | None    |                                                                                          |
| ELASTIC_APM_SECRET_TOKEN   | None    |                                                                                          |
| HALO_SUBDOMAIN             | None    | Halo help desk subdomain                                                                 |
| REQUIRE_ZENDESK            | false   | Control whether Zendesk credentials are required when creating `HelpDeskCreds` instances |
| EMAIL_ROUTER_ZENDESK_TOKEN | None    | Zendesk token used by Lambda function to connect to API                                  |
| EMAIL_ROUTER_ZENDESK_EMAIL | None    | Zendesk account email address used by Lambda function to connect to API                  |
| EMAIL_ROUTER_API_URL       | None    | Zendesk API URL used by Lambda function                                                  |
