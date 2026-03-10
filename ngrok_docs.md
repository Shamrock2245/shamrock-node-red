# ngrok Documentation
> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# OAuth Action

> The OAuth action restricts access to only authorized users by enforcing OAuth through an identity provider of your choice.

export const YouTubeEmbed = ({className, title, videoId, ...props}) => {
  return <div className={`relative aspect-video mb-3 ${className}`} {...props}>
      <iframe src={`https://www.youtube.com/embed/${videoId}`} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen className="absolute inset-0 w-full h-full" title={title} />
    </div>;
};

export const ConfigChildren = ({children}) => {
  return <Accordion title="Show Child Properties">
      {children}
    </Accordion>;
};

export const ConfigField = ({title, type, cel = false, defaultValue = false, required = false, children}) => {
  const id = `config-${title.replace(/\.|\s|\*/g, "_")}`;
  return <div className="field pt-2.5 pb-5 my-2.5 border-gray-50 dark:border-gray-800/50 border-b" style={{
    scrollMarginTop: '120px'
  }} id={id}>
      <div className="flex font-mono group/param-head param-head break-all relative">
        <div className="flex-1 flex content-start py-0.5 mr-5">
          <div className="flex items-center flex-wrap gap-2">
            <div class="absolute -top-1.5">
              <a href={`#${id}`} className="-ml-10 flex items-center opacity-0 border-0 group-hover/param-head:opacity-100 py-2 [.expandable-content_&]:-ml-[2.1rem]" aria-label="Navigate to header">
                ​<div className="w-6 h-6 rounded-md flex items-center justify-center shadow-sm text-gray-400 dark:text-white/50 dark:bg-background-dark dark:brightness-[1.35] dark:ring-1 dark:hover::rightness-150 bg-white ring-1 ring-gray-400/30 dark:ring-gray-700/25 hover:ring-gray-400/60 dark:hover:ring-white/20">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="gray" height="12px" viewBox="0 0 576 512"><path d="M0 256C0 167.6 71.6 96 160 96h72c13.3 0 24 10.7 24 24s-10.7 24-24 24H160C98.1 144 48 194.1 48 256s50.1 112 112 112h72c13.3 0 24 10.7 24 24s-10.7 24-24 24H160C71.6 416 0 344.4 0 256zm576 0c0 88.4-71.6 160-160 160H344c-13.3 0-24-10.7-24-24s10.7-24 24-24h72c61.9 0 112-50.1 112-112s-50.1-112-112-112H344c-13.3 0-24-10.7-24-24s10.7-24 24-24h72c88.4 0 160 71.6 160 160zM184 232H392c13.3 0 24 10.7 24 24s-10.7 24-24 24H184c-13.3 0-24-10.7-24-24s10.7-24 24-24z"></path></svg>
                </div>
              </a>
            </div>
            <div className="font-semibold text-primary dark:text-primary-light overflow-wrap-anywhere">{title}</div>
            <div className="inline items-center gap-2 text-xs font-medium [&_div]:inline [&_div]:mr-2 [&_div]:leading-5 [&_a]:inline [&_a]:mr-2 [&_a]:leading-5">
              {type && <div className="flex items-center px-2 py-0.5 rounded-md bg-gray-100/50 dark:bg-white/5 break-all">
                <span className="text-gray-600 dark:text-gray-200 !font-medium">{type}</span>
              </div>}
              {defaultValue && <div className="flex items-center px-2 py-0.5 rounded-md bg-gray-100/50 dark:bg-white/5 break-all">
                  <span class="text-gray-400 dark:text-gray-500">default:</span>
                  <span className="text-gray-600 dark:text-gray-200 !font-medium">{defaultValue}</span>
                </div>}
              {required && <div className="px-2 py-0.5 rounded-md bg-red-100/50 dark:bg-red-400/10 whitespace-nowrap">
                <span className="text-red-600 dark:text-red-300 !font-medium">Required</span>
              </div>}
              {cel && <a className="px-2 py-0.5 rounded-md !border-none bg-blue-100/50 dark:bg-blue-400/10 whitespace-nowrap" href="/traffic-policy/concepts/cel-interpolation">
                <span className="text-blue-600 dark:text-blue-300 !font-medium">Supports CEL</span>
              </a>}
            </div>
          </div>
        </div>
      </div>
      <div className="mt-4 prose-sm prose-gray dark:prose-invert [&_.prose>p:first-child]:mt-0 [&_.prose>p:last-child]:mb-0">
        {children}
      </div>
    </div>;
};

<Note>
  This page relates to requiring OAuth for visitors to access your endpoints.
  To configure OAuth and SSO providers for signing into the ngrok dashboard, see [the dashboard SSO documentation](/iam/sso).
</Note>

The OAuth Traffic Policy action restricts access to your endpoints to only authorized users by enforcing OAuth through an identity provider of your choice.

<YouTubeEmbed videoId="yGf_OdknZkM" title="OAuth Traffic Policy action" />

## Configuration reference

The [Traffic Policy](/traffic-policy/) configuration reference for this action.

### Supported phases

`on_http_request`

### Type

`oauth`

### Configuration fields

<ConfigField title="provider" type="string" required={true}>
  The name of the *OAuth* identity provider to be used for authentication.
</ConfigField>

<ConfigField title="auth_id" type="string" required={false}>
  Unique authentication identifier for this provider.
  This value is used for the cookie, redirect, authentication, and logout purposes.

  <Note>
    To log in a user you must use `/ngrok/login?auth_id={auth_id}`.
    If you're using path-based auth you must include the path to be redirected back to: `?redirect_path=/foo`
  </Note>
</ConfigField>

<ConfigField title="client_id" type="string" required={false} cel={true}>
  Your OAuth app's client ID.

  <Note>
    Leave this empty if you want to use ngrok's managed application.
  </Note>
</ConfigField>

<ConfigField title="client_secret" type="string" required={false} cel={true}>
  Your OAuth app's client secret.

  <Note>
    Leave this empty if you want to use a managed application.
  </Note>
</ConfigField>

<ConfigField title="scopes" type="array of strings" required={false}>
  A list of additional scopes to request when users authenticate with the identity provider.
</ConfigField>

<ConfigField title="authz_url_params" type="map of string to string" required={false}>
  A map of additional URL parameters to apply to the authorization endpoint URL.
</ConfigField>

<ConfigField title="max_session_duration" type="duration" required={false}>
  Defines the maximum lifetime of a session regardless of activity.
</ConfigField>

<ConfigField title="idle_session_timeout" type="duration" required={false}>
  Defines the period of inactivity after which a user's session is automatically ended, requiring re-authentication.
</ConfigField>

<ConfigField title="userinfo_refresh_interval" type="duration" required={false}>
  How often should ngrok refresh data about the authenticated user from the identity provider.
</ConfigField>

<ConfigField title="allow_cors_preflight" type="boolean" required={false} defaultValue={false}>
  Allow CORS preflight requests to bypass authentication checks.
  Enable this if the endpoint needs to be accessible via CORS.
</ConfigField>

<ConfigField title="auth_cookie_domain" type="string" required={false}>
  Sets the allowed domain for the auth cookie.
</ConfigField>

### Special paths

#### `/ngrok/login`

Redirect users to this path to explicitly begin an authentication flow.
After authentication, users will be redirected to `/`.
If the IdP supports it, ngrok will attempt to instruct the IdP to force re-authentication which will force users to re-enter their credentials with the IdP even if they were already logged in.

#### `/ngrok/logout`

Logs the user out by clearing their session cookie.
Redirect users to this path to log them out.

<Note>
  When using the Google OAuth 2.0/OIDC provider in Chrome with a [managed profile](https://support.google.com/chrome/a/answer/188446), `/ngrok/logout` only clears the ngrok session cookie; it does not end the Google/IdP session maintained by the browser.
  Users may be silently re-authenticated on the next request.
  To fully sign out, sign out of Chrome/Google (or use a non-managed profile or Incognito) in addition to calling `/ngrok/logout`.
</Note>

### Events

When this action is enabled, it populates the following fields in the [`http_request_complete.v0`](/obs/events/reference/#http-request-complete) event:

* `oauth.app_client_id`
* `oauth.decision`
* `oauth.user.id`
* `oauth.user.name`

### Supported providers

ngrok currently supports the following OAuth providers (see the Integration Guides for more details).
In some instances, ngrok has a [managed application](#managed-applications) that allows you to configure OAuth without setting up your own application in your provider.
This is useful for testing and development, but when you move into production, use your own custom application in your specific provider.

| Provider  | Provider Identifier | Managed App Available | Integration Guide                                    |
| --------- | ------------------- | --------------------- | ---------------------------------------------------- |
| Amazon    | `amazon`            | no                    | [Documentation](/integrations/oauth/oauth/)          |
| Facebook  | `facebook`          | no                    | [Documentation](/integrations/oauth/facebook-oauth)  |
| GitHub    | `github`            | yes                   | [Documentation](/integrations/oauth/github-oauth)    |
| GitLab    | `gitlab`            | yes                   | [Documentation](/integrations/oauth/gitlab-oauth)    |
| Google    | `google`            | yes                   | [Documentation](/integrations/oauth/google-oauth)    |
| LinkedIn  | `linkedin`          | yes                   | [Documentation](/integrations/oauth/linkedin-oauth)  |
| Microsoft | `microsoft`         | yes                   | [Documentation](/integrations/oauth/microsoft-oauth) |
| Twitch    | `twitch`            | yes                   | [Documentation](/integrations/oauth/twitch-oauth)    |

### Required scopes

This is a list of the minimum required scopes for each provider.
You can use this when configuring your identity provider.
These are not required when using the ngrok managed applications.

| Provider  | Scopes                                                                                               |
| --------- | ---------------------------------------------------------------------------------------------------- |
| Amazon    | `profile`                                                                                            |
| Facebook  | `email`                                                                                              |
| Github    | `read:org`, `read:user`                                                                              |
| Gitlab    | `email`, `openid`, `profile`                                                                         |
| Google    | `https://www.googleapis.com/auth/userinfo.email`, `https://www.googleapis.com/auth/userinfo.profile` |
| LinkedIn  | `r_emailaddress`, `r_liteprofile`                                                                    |
| Microsoft | `User.Read`                                                                                          |
| Twitch    | `user:read:email`                                                                                    |

## Try it out

See the list of [supported providers](#supported-providers) for step-by-step integration guides.

## Behavior

### Callback URL

When you create your own OAuth app, you must specify a callback (or redirect) URL to the OAuth provider.
When using ngrok's OAuth action, the callback URL is always:

```
https://idp.ngrok.com/oauth2/callback
```

### Authentication

When an unauthenticated request is made to an OAuth-protected endpoint, it returns a redirect response that begins an authentication flow with the configured identity provider.
The original URI path is saved so that users can be redirected to it if they successfully authenticate.

**If the user fails to authenticate with the identity provider**, ngrok will display an error describing the failure returned by the identity provider and prompt them to try logging in again.

**If the user successfully authenticates with the identity provider**, ngrok will take the following actions:

* Sets a [session cookie](#cookies) to avoid repeating the authentication flow again.
* Redirects the user to the original URI path they were attempting to access before the authentication flow began.
  If no such URI path was captured, they are redirected to `/`.
* Continue processing the rest of the Traffic Policy actions.

### Continuous authorization

When an authenticated user makes a request, ngrok will sometimes refresh a user's data from the identity provider (email, name, etc.) and re-evaluate authorization constraints.
This refresh is executed as a back channel request to the identity provider; it is transparent to the user and they do not go through a re-authentication flow.

The following circumstances trigger refresh and authorization re-evaluation:

* On a periodic interval defined by the [`userinfo_refresh_interval`](/traffic-policy/actions/oauth/#configuration-fields) parameter.
* If you update the OAuth configuration of the endpoint either in the agent or through the dashboard.
* If you update the OAuth configuration of the endpoint.

If a previously authenticated user becomes unauthorized because their identity provider information changed or because the OAuth action configuration changed, they are presented an error and are prompted to try logging in again.

### Managed applications

Managed applications allow you to use ngrok's OAuth action without setting up your own OAuth apps with the identity providers.
More practically, this means you can use the OAuth action without configuring a client id and client secret.

Managed applications are great for getting started but they have some limitations.

* They are [only available for some identity providers](#supported-providers).
* You may not pass custom scopes when using a managed application.
* The [upstream headers](/universal-gateway/http/#upstream-headers) `ngrok-auth-oauth-access-token` and `ngrok-auth-oauth-refresh-token` are not sent to your application.

### Traffic identities

ngrok's [Traffic Identities](/traffic-policy/identities/) feature can be used to observe
all of the authenticated user activity across your account in the ngrok
dashboard or via API. Whenever a user authenticates or accesses an endpoint
with a configured OIDC action, their Traffic Identity record is created or updated.

You may also use Traffic Identities to remotely log a user out by [revoking a
session](/traffic-policy/identities/#revoke-sessions).

### Cookies

This action sets two cookies in its operation.
Cookie values are opaque to the upstream service and must not be modified.

| Cookie    | Description                             |
| --------- | --------------------------------------- |
| `session` | Used to track an authenticated user.    |
| `nonce`   | Used to secure the authentication flow. |

### Non-terminating action

This is a **Non-terminating action**. It does not return a response, and will allow Traffic Policy processing to continue to the next Action in the chain. All **Cloud Endpoint** Traffic Policies must end with a terminating action. This requirement does not apply to **Agent Endpoints**.

## Examples

### Using a managed provider

The following [Traffic Policy](/traffic-policy/) configuration will provide your app with a Google authentication step.

<CodeGroup>
  ```yaml policy.yml theme={null}
  on_http_request:
    - actions:
        - type: oauth
          config:
            provider: google
  ```

  ```json policy.json theme={null}
  {
    "on_http_request": [
      {
        "actions": [
          {
            "type": "oauth",
            "config": {
              "provider": "google"
            }
          }
        ]
      }
    ]
  }
  ```
</CodeGroup>

You can replace the `provider` value with any of the [supported providers](/traffic-policy/actions/oauth/#supported-providers) that have a managed app available.

### Restricting access to certain users

See [this authentication example](/traffic-policy/examples/add-authentication/#conditional-access-using-oauth-variables) to learn how to restrict access based on OAuth result variables.

### Using a Custom Provider

If you need more control than what a managed provider can offord you then you
can bring your own provider.

#### Google Example

#### GitHub Example

<CodeGroup>
  ```yaml policy.yml theme={null}
  on_http_request:
    - actions:
        - type: oauth
          config:
            provider: github
            client_id: '{your app''s oauth client id}'
            client_secret: '{your app''s oauth client secret}'
            scopes:
              - read:user
              - read:org
  ```

  ```json policy.json theme={null}
  {
    "on_http_request": [
      {
        "actions": [
          {
            "type": "oauth",
            "config": {
              "provider": "github",
              "client_id": "{your app's oauth client id}",
              "client_secret": "{your app's oauth client secret}",
              "scopes": [
                "read:user",
                "read:org"
              ]
            }
          }
        ]
      }
    ]
  }
  ```
</CodeGroup>

#### GitLab Example

<CodeGroup>
  ```yaml policy.yml theme={null}
  on_http_request:
    - actions:
        - type: oauth
          config:
            provider: gitlab
            client_id: '{your app''s oauth client id}'
            client_secret: '{your app''s oauth client secret}'
            scopes:
              - openid
              - profile
              - email
  ```

  ```json policy.json theme={null}
  {
    "on_http_request": [
      {
        "actions": [
          {
            "type": "oauth",
            "config": {
              "provider": "gitlab",
              "client_id": "{your app's oauth client id}",
              "client_secret": "{your app's oauth client secret}",
              "scopes": [
                "openid",
                "profile",
                "email"
              ]
            }
          }
        ]
      }
    ]
  }
  ```
</CodeGroup>

#### LinkedIn Example

<CodeGroup>
  ```yaml policy.yml theme={null}
  on_http_request:
    - actions:
        - type: oauth
          config:
            provider: linkedin
            client_id: '{your app''s oauth client id}'
            client_secret: '{your app''s oauth client secret}'
            scopes:
              - r_emailaddress
              - r_liteprofile
  ```

  ```json policy.json theme={null}
  {
    "on_http_request": [
      {
        "actions": [
          {
            "type": "oauth",
            "config": {
              "provider": "linkedin",
              "client_id": "{your app's oauth client id}",
              "client_secret": "{your app's oauth client secret}",
              "scopes": [
                "r_emailaddress",
                "r_liteprofile"
              ]
            }
          }
        ]
      }
    ]
  }
  ```
</CodeGroup>

#### Microsoft Example

<CodeGroup>
  ```yaml policy.yml theme={null}
  on_http_request:
    - actions:
        - type: oauth
          config:
            provider: microsoft
            client_id: '{your app''s oauth client id}'
            client_secret: '{your app''s oauth client secret}'
            scopes:
              - openid
              - email
              - profile
  ```

  ```json policy.json theme={null}
  {
    "on_http_request": [
      {
        "actions": [
          {
            "type": "oauth",
            "config": {
              "provider": "microsoft",
              "client_id": "{your app's oauth client id}",
              "client_secret": "{your app's oauth client secret}",
              "scopes": [
                "openid",
                "email",
                "profile"
              ]
            }
          }
        ]
      }
    ]
  }
  ```
</CodeGroup>

#### Twitch Example

<CodeGroup>
  ```yaml policy.yml theme={null}
  on_http_request:
    - actions:
        - type: oauth
          config:
            provider: twitch
            client_id: '{your app''s oauth client id}'
            client_secret: '{your app''s oauth client secret}'
            scopes:
              - user:read:email
              - openid
  ```

  ```json policy.json theme={null}
  {
    "on_http_request": [
      {
        "actions": [
          {
            "type": "oauth",
            "config": {
              "provider": "twitch",
              "client_id": "{your app's oauth client id}",
              "client_secret": "{your app's oauth client secret}",
              "scopes": [
                "user:read:email",
                "openid"
              ]
            }
          }
        ]
      }
    ]
  }
  ```
</CodeGroup>

#### Amazon Example

<CodeGroup>
  ```yaml policy.yml theme={null}
  on_http_request:
    - actions:
        - type: oauth
          config:
            provider: amazon
            client_id: '{your app''s oauth client id}'
            client_secret: '{your app''s oauth client secret}'
            scopes:
              - profile
  ```

  ```json policy.json  theme={null}
  {
    "on_http_request": [
      {
        "actions": [
          {
            "type": "oauth",
            "config": {
              "provider": "amazon",
              "client_id": "{your app's oauth client id}",
              "client_secret": "{your app's oauth client secret}",
              "scopes": [
                "profile"
              ]
            }
          }
        ]
      }
    ]
  }
  ```
</CodeGroup>

#### Facebook Example

<CodeGroup>
  ```yaml policy.yml theme={null}
  on_http_request:
    - actions:
        - type: oauth
          config:
            provider: facebook
            client_id: '{your app''s oauth client id}'
            client_secret: '{your app''s oauth client secret}'
            scopes:
              - email
  ```

  ```json policy.json theme={null}
  {
    "on_http_request": [
      {
        "actions": [
          {
            "type": "oauth",
            "config": {
              "provider": "facebook",
              "client_id": "{your app's oauth client id}",
              "client_secret": "{your app's oauth client secret}",
              "scopes": [
                "email"
              ]
            }
          }
        ]
      }
    ]
  }
  ```
</CodeGroup>

## Action result variables

The following variables are made available for use in subsequent expressions and
CEL interpolations after the action has run. Variable values will only apply
to the last action execution, results are not concatenated.

<ConfigField title="actions.ngrok.oauth.error.code" type="string">
  Code for an error that occurred during the invocation of an action.
</ConfigField>

<ConfigField title="actions.ngrok.oauth.error.message" type="string">
  Message for an error that occurred during the invocation of an action.
</ConfigField>

<ConfigField title="actions.ngrok.oauth.identity.id" type="string">
  Unique identifier for the ngrok Identity entity.
</ConfigField>

<ConfigField title="actions.ngrok.oauth.identity.email" type="string">
  Email address of the authorized user from the provider.
</ConfigField>

<ConfigField title="actions.ngrok.oauth.identity.name" type="string">
  Name for the authorized user from the provider.
</ConfigField>

<ConfigField title="actions.ngrok.oauth.identity.provider_user_id" type="string">
  Identifier for the authorized user from the provider.
</ConfigField>

<ConfigField title="actions.ngrok.oauth.identity.current_provider_session_id" type="string">
  The current Identity session identifier for this request.
</ConfigField>

<ConfigField title="actions.ngrok.oauth.access_token" type="string">
  The access token from the provider.
</ConfigField>

<ConfigField title="actions.ngrok.oauth.refresh_token" type="string">
  The refresh token from the provider.
</ConfigField>

<ConfigField title="actions.ngrok.oauth.expires_at" type="string">
  Timestamp when the current session will expire.
</ConfigField>

<ConfigField title="actions.ngrok.oauth.session_timed_out" type="boolean">
  Returns true when the session timed out.
</ConfigField>

<ConfigField title="actions.ngrok.oauth.session_max_duration_reached" type="boolean">
  Returns true when the current session reached the max duration.
</ConfigField>

<ConfigField title="actions.ngrok.oauth.userinfo_refreshed" type="boolean">
  Returns true when ngrok updates the user information on the identity.
</ConfigField>


Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Getting Started with Agent Endpoints and Traffic Policy via CLI Flags

> Learn how to set up an Agent Endpoint with a custom Traffic Policy using the ngrok agent CLI.

## What you'll need

* An [ngrok account](https://dashboard.ngrok.com/).
* The [ngrok Agent CLI](https://ngrok.com/download) installed.

## 1. Create a Traffic Policy

Create a custom Traffic Policy file with the following contents:

```yaml  theme={null}
on_http_request:
  - actions:
      - type: custom-response
        config:
          status_code: 200
          body: "Hello, World!"
```

This policy will respond to each HTTP request with a simple “Hello, World!” message.

## 2. Apply your Traffic Policy

Run the agent, applying the Traffic Policy you saved in the previous step with the `--traffic-policy-file` flag:

```
$ ngrok http 80 --traffic-policy-file policy.yml
```

This command starts an HTTP tunnel for port `80`, using the specified `policy.yml` Traffic Policy to manage traffic.

## 3. Test it out

After running the ngrok command in the previous step you should now see a URL in the forwarding section. Open the URL
in your web browser. You should see the "Hello, World!" message displayed in your browser.

## What's next?

You've now successfully set up your first Agent Endpoint with a custom Traffic Policy using the ngrok agent.

To learn more about ngrok's Traffic Policy and its capabilities, check out the following resources:

* Learn about the [core concepts](/traffic-policy/concepts/) like phases and rules.
* Check out the [examples, use-cases and guides](/traffic-policy/examples/a-b-tests/).
* The list of [available actions](/traffic-policy/actions/), [macros](/traffic-policy/macros/) and [variables](/traffic-policy/variables/) you can use.


Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Getting Started with Agent Endpoints and Traffic Policy via CLI Flags

> Learn how to set up an Agent Endpoint with a custom Traffic Policy using the ngrok agent CLI.

## What you'll need

* An [ngrok account](https://dashboard.ngrok.com/).
* The [ngrok Agent CLI](https://ngrok.com/download) installed.

## 1. Create a Traffic Policy

Create a custom Traffic Policy file with the following contents:

```yaml  theme={null}
on_http_request:
  - actions:
      - type: custom-response
        config:
          status_code: 200
          body: "Hello, World!"
```

This policy will respond to each HTTP request with a simple “Hello, World!” message.

## 2. Apply your Traffic Policy

Run the agent, applying the Traffic Policy you saved in the previous step with the `--traffic-policy-file` flag:

```
$ ngrok http 80 --traffic-policy-file policy.yml
```

This command starts an HTTP tunnel for port `80`, using the specified `policy.yml` Traffic Policy to manage traffic.

## 3. Test it out

After running the ngrok command in the previous step you should now see a URL in the forwarding section. Open the URL
in your web browser. You should see the "Hello, World!" message displayed in your browser.

## What's next?

You've now successfully set up your first Agent Endpoint with a custom Traffic Policy using the ngrok agent.

To learn more about ngrok's Traffic Policy and its capabilities, check out the following resources:

* Learn about the [core concepts](/traffic-policy/concepts/) like phases and rules.
* Check out the [examples, use-cases and guides](/traffic-policy/examples/a-b-tests/).
* The list of [available actions](/traffic-policy/actions/), [macros](/traffic-policy/macros/) and [variables](/traffic-policy/variables/) you can use.


Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Getting Started with Agent Endpoints and Traffic Policy via CLI Flags

> Learn how to set up an Agent Endpoint with a custom Traffic Policy using the ngrok agent CLI.

## What you'll need

* An [ngrok account](https://dashboard.ngrok.com/).
* The [ngrok Agent CLI](https://ngrok.com/download) installed.

## 1. Create a Traffic Policy

Create a custom Traffic Policy file with the following contents:

```yaml  theme={null}
on_http_request:
  - actions:
      - type: custom-response
        config:
          status_code: 200
          body: "Hello, World!"
```

This policy will respond to each HTTP request with a simple “Hello, World!” message.

## 2. Apply your Traffic Policy

Run the agent, applying the Traffic Policy you saved in the previous step with the `--traffic-policy-file` flag:

```
$ ngrok http 80 --traffic-policy-file policy.yml
```

This command starts an HTTP tunnel for port `80`, using the specified `policy.yml` Traffic Policy to manage traffic.

## 3. Test it out

After running the ngrok command in the previous step you should now see a URL in the forwarding section. Open the URL
in your web browser. You should see the "Hello, World!" message displayed in your browser.

## What's next?

You've now successfully set up your first Agent Endpoint with a custom Traffic Policy using the ngrok agent.

To learn more about ngrok's Traffic Policy and its capabilities, check out the following resources:

* Learn about the [core concepts](/traffic-policy/concepts/) like phases and rules.
* Check out the [examples, use-cases and guides](/traffic-policy/examples/a-b-tests/).
* The list of [available actions](/traffic-policy/actions/), [macros](/traffic-policy/macros/) and [variables](/traffic-policy/variables/) you can use.


Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# IP Policies

> Use rules to allow or deny traffic and dashboard access from specific IPs and CIDRs.

IP Policies are reusable groups of rules for allowing or denying traffic and ngrok dashboard access from specific IPs and CIDRs. You can enforce them in the following scenarios:

## Applying IP Policies to Endpoints

You can add an IP Policy to your endpoints using the [`restrict-ips`](/traffic-policy/actions/restrict-ips) Traffic Policy Action.

To get started with an Agent Endpoint, create a `policy.yml` or `policy.json` file on the same machine as the endpoint. To use a Cloud Endpoint, [visit the Endpoints section in the ngrok dashboard](https://dashboard.ngrok.com/endpoints) and select the Cloud Endpoint. You'll be taken to the Traffic Policy editor.

The contents of the policy file should be the following:

<CodeGroup>
  ```yaml policy.yml theme={null}
  on_http_request:
    # Only allow requests from trusted IPs
    - actions:
        - type: restrict-ips
          config:
            allow:
              - 203.0.113.0/24
              - 198.51.100.42/32
  ```

  ```json policy.json theme={null}
  {
    "on_http_request": [
      {
        "actions": [
          {
            "type": "restrict-ips",
            "config": {
              "allow": [
                "203.0.113.0/24",
                "198.51.100.42/32"
              ]
            }
          }
        ]
      }
    ]
  }
  ```
</CodeGroup>

If you're using a Cloud Endpoint, save your changes in the dashboard. To apply this policy to your Agent Endpoint, start it using the `--traffic-policy-file` flag as shown in the following example:

```bash  theme={null}
ngrok http $YOUR_PORT --url $YOUR_DOMAIN --traffic-policy-file /path/to/policy.yml
```

## Applying account-wide IP Policies

To apply account-wide IP Policies, you can use [the IP Restrictions feature in the ngrok dashboard](https://dashboard.ngrok.com/ip-restrictions).

In the dashboard UI, you can apply [IP Restrictions](/traffic-policy/examples/add-authentication#ip-restrictions) to users trying to sign in to your ngrok dashboard, traffic trying to access your API or Endpoints, and source IPs trying to start Agent Endpoints on your account.

You can define the IP Policies that make up your restrictions in the dashboard UI.


Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Verify Webhook Action

> Validate incoming webhook signatures against a known secret to ensure authenticity.

export const ConfigChildren = ({children}) => {
  return <Accordion title="Show Child Properties">
      {children}
    </Accordion>;
};

export const ConfigField = ({title, type, cel = false, defaultValue = false, required = false, children}) => {
  const id = `config-${title.replace(/\.|\s|\*/g, "_")}`;
  return <div className="field pt-2.5 pb-5 my-2.5 border-gray-50 dark:border-gray-800/50 border-b" style={{
    scrollMarginTop: '120px'
  }} id={id}>
      <div className="flex font-mono group/param-head param-head break-all relative">
        <div className="flex-1 flex content-start py-0.5 mr-5">
          <div className="flex items-center flex-wrap gap-2">
            <div class="absolute -top-1.5">
              <a href={`#${id}`} className="-ml-10 flex items-center opacity-0 border-0 group-hover/param-head:opacity-100 py-2 [.expandable-content_&]:-ml-[2.1rem]" aria-label="Navigate to header">
                ​<div className="w-6 h-6 rounded-md flex items-center justify-center shadow-sm text-gray-400 dark:text-white/50 dark:bg-background-dark dark:brightness-[1.35] dark:ring-1 dark:hover::rightness-150 bg-white ring-1 ring-gray-400/30 dark:ring-gray-700/25 hover:ring-gray-400/60 dark:hover:ring-white/20">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="gray" height="12px" viewBox="0 0 576 512"><path d="M0 256C0 167.6 71.6 96 160 96h72c13.3 0 24 10.7 24 24s-10.7 24-24 24H160C98.1 144 48 194.1 48 256s50.1 112 112 112h72c13.3 0 24 10.7 24 24s-10.7 24-24 24H160C71.6 416 0 344.4 0 256zm576 0c0 88.4-71.6 160-160 160H344c-13.3 0-24-10.7-24-24s10.7-24 24-24h72c61.9 0 112-50.1 112-112s-50.1-112-112-112H344c-13.3 0-24-10.7-24-24s10.7-24 24-24h72c88.4 0 160 71.6 160 160zM184 232H392c13.3 0 24 10.7 24 24s-10.7 24-24 24H184c-13.3 0-24-10.7-24-24s10.7-24 24-24z"></path></svg>
                </div>
              </a>
            </div>
            <div className="font-semibold text-primary dark:text-primary-light overflow-wrap-anywhere">{title}</div>
            <div className="inline items-center gap-2 text-xs font-medium [&_div]:inline [&_div]:mr-2 [&_div]:leading-5 [&_a]:inline [&_a]:mr-2 [&_a]:leading-5">
              {type && <div className="flex items-center px-2 py-0.5 rounded-md bg-gray-100/50 dark:bg-white/5 break-all">
                <span className="text-gray-600 dark:text-gray-200 !font-medium">{type}</span>
              </div>}
              {defaultValue && <div className="flex items-center px-2 py-0.5 rounded-md bg-gray-100/50 dark:bg-white/5 break-all">
                  <span class="text-gray-400 dark:text-gray-500">default:</span>
                  <span className="text-gray-600 dark:text-gray-200 !font-medium">{defaultValue}</span>
                </div>}
              {required && <div className="px-2 py-0.5 rounded-md bg-red-100/50 dark:bg-red-400/10 whitespace-nowrap">
                <span className="text-red-600 dark:text-red-300 !font-medium">Required</span>
              </div>}
              {cel && <a className="px-2 py-0.5 rounded-md !border-none bg-blue-100/50 dark:bg-blue-400/10 whitespace-nowrap" href="/traffic-policy/concepts/cel-interpolation">
                <span className="text-blue-600 dark:text-blue-300 !font-medium">Supports CEL</span>
              </a>}
            </div>
          </div>
        </div>
      </div>
      <div className="mt-4 prose-sm prose-gray dark:prose-invert [&_.prose>p:first-child]:mt-0 [&_.prose>p:last-child]:mb-0">
        {children}
      </div>
    </div>;
};

The **Verify Webhook** Traffic Policy action enables you to validate incoming webhook signatures against a known secret to ensure authenticity. Depending on the verification result, it either forwards the request to the next action or rejects it, safeguarding your endpoints from unauthorized or tampered webhooks.

## Configuration reference

This is the [Traffic Policy](/traffic-policy/) configuration
reference for this action.

### Supported directions

* `on_http_request`

### Type

`verify-webhook`

### Configuration fields

<ConfigField title="provider" type="string" required={true}>
  <p>The name of the provider to verify webhook requests from.</p>
  <p>Value must be a [supported provider](#supported-providers) identifier.</p>
</ConfigField>

<ConfigField title="secret" type="string" required={true} cel={true}>
  <p>The secret key used to validate webhook requests from the specified provider.</p>
  <p>Supports [CEL Interpolation](/traffic-policy/concepts/cel-interpolation).</p>
</ConfigField>

<ConfigField title="enforce" type="bool" required={false}>
  <p>When `true`, the request will be halted if the webhook is not valid and no further actions will run. However when `false`, subsequent actions will run even if the webhook was not valid.</p>
  <p>Default <code>true</code>.</p>
</ConfigField>

## Behavior

The **verify-webhook** action ensures the authenticity of incoming webhook requests by validating their signatures against a known secret. Upon receiving a request, the action performs the signature verification. If verification succeeds, the request proceeds through the action chain. If it fails, the request is terminated with a `403 Forbidden` response, unless `enforce` is set to `false`, in which case the request proceeds without termination.

### Verification process

* **Signature Validation**: The action validates incoming webhook signature to confirm the request originates from the configured provider and that the payload has not been tampered with.
* **Request Handling**: If the webhook verification is successful, the request is forwarded to the next action. If the verification fails, the request chain is terminated with a `403` response.
* **Configurable Enforcement**: By default, verification failures result in termination. However, setting `enforce: false` allows unverified requests to proceed, while logging the verification result. This option is useful for debugging, testing, and crafting your own custom responses with action result variables.

### Endpoint verification

Some webhook providers require an initial endpoint verification challenge to validate that your application is legitimate before sending webhook events. The **verify-webhook** action automatically handles endpoint verification challenges for supported providers.

* Supported providers:
  * Twitter
  * Worldline
  * Xero
  * Zoom

#### Replay prevention with timestamp tolerance

To prevent replay attacks, ngrok verifies that the webhook’s timestamp falls within an acceptable range.

#### Secret handling and encryption

All secrets used for webhook verification are encrypted at config validation. When ngrok processes a requests the secret is decrypted.

### Non-terminating action

This is a **Non-terminating action**. It does not return a response, and will allow Traffic Policy processing to continue to the next Action in the chain. All **Cloud Endpoint** Traffic Policies must end with a terminating action. This requirement does not apply to **Agent Endpoints**.

## Supported providers

Currently, these integration guides refer to modules.

| Provider                    | Provider Identifier     | Integration Guide                                                                                    |
| --------------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------- |
| AfterShip                   | `aftership`             | [Documentation](/integrations/webhooks/aftership-webhooks)                                           |
| Airship                     | `airship`               | [Documentation](/integrations/webhooks/airship-webhooks)                                             |
| Alchemy                     | `alchemy`               | [Documentation](https://docs.alchemy.com/reference/notify-api-quickstart)                            |
| Amazon SNS                  | `sns`                   | [Documentation](/integrations/webhooks/amazon-sns-webhooks)                                          |
| Autodesk Platform Services  | `autodesk`              | [Documentation](/integrations/webhooks/autodesk-webhooks)                                            |
| Bitbucket                   | `bitbucket`             | [Documentation](/integrations/webhooks/bitbucket-webhooks)                                           |
| Bolt                        | `bolt`                  | [Documentation](https://help.bolt.com/developers/guides/webhooks/hook-verification/)                 |
| Box                         | `box`                   | [Documentation](/integrations/webhooks/box-webhooks)                                                 |
| Brex                        | `brex`                  | [Documentation](/integrations/webhooks/brex-webhooks)                                                |
| Buildkite                   | `buildkite`             | [Documentation](/integrations/webhooks/buildkite-webhooks)                                           |
| Calendly                    | `calendly`              | [Documentation](/integrations/webhooks/calendly-webhooks)                                            |
| Castle                      | `castle`                | [Documentation](/integrations/webhooks/castle-webhooks)                                              |
| Chargify                    | `chargify`              | [Documentation](/integrations/webhooks/chargify-webhooks)                                            |
| CircleCI                    | `circleci`              | [Documentation](/integrations/webhooks/circleci-webhooks)                                            |
| Clearbit                    | `clearbit`              | [Documentation](/integrations/webhooks/clearbit-webhooks)                                            |
| Clerk                       | `clerk`                 | [Documentation](/integrations/webhooks/clerk-webhooks)                                               |
| Coinbase                    | `coinbase`              | [Documentation](/integrations/webhooks/coinbase-webhooks)                                            |
| Contentful                  | `contentful`            | [Documentation](/integrations/webhooks/contentful-webhooks)                                          |
| DocuSign                    | `docusign`              | [Documentation](/integrations/webhooks/docusign-webhooks)                                            |
| Dropbox                     | `dropbox`               | [Documentation](/integrations/webhooks/dropbox-webhooks)                                             |
| Facebook Graph API          | `facebook_graph_api`    | [Documentation](/integrations/webhooks/facebook-webhooks)                                            |
| Facebook Messenger          | `facebook_messenger`    | [Documentation](/integrations/webhooks/facebook-messenger-webhooks)                                  |
| Frame.io                    | `frameio`               | [Documentation](/integrations/webhooks/frameio-webhooks)                                             |
| GitHub                      | `github`                | [Documentation](/integrations/webhooks/github-webhooks)                                              |
| GitLab                      | `gitlab`                | [Documentation](/integrations/webhooks/gitlab-webhooks)                                              |
| Go1                         | `go1`                   | [Documentation](https://www.go1.com/developers/partners/concepts/webhook-signature-authentification) |
| Heroku                      | `heroku`                | [Documentation](/integrations/webhooks/heroku-webhooks)                                              |
| Hosted Hooks                | `hostedhooks`           | [Documentation](/integrations/webhooks/hostedhooks-webhooks)                                         |
| HubSpot                     | `hubspot`               | [Documentation](/integrations/webhooks/hubspot-webhooks)                                             |
| Hygraph (Formerly GraphCMS) | `graphcms`              | [Documentation](/integrations/webhooks/hygraph-webhooks)                                             |
| Instagram                   | `instagram`             | [Documentation](/integrations/webhooks/instagram-webhooks)                                           |
| Intercom                    | `intercom`              | [Documentation](/integrations/webhooks/intercom-webhooks)                                            |
| Jira                        | `jira`                  | [Documentation](/integrations/webhooks/jira-webhooks)                                                |
| Launch Darkly               | `launch_darkly`         | [Documentation](/integrations/webhooks/launchdarkly-webhooks)                                        |
| Linear                      | `linear`                | [Documentation](/integrations/webhooks/linear-webhooks)                                              |
| Mailchimp                   | `mailchimp`             | [Documentation](/integrations/webhooks/mailchimp-webhooks)                                           |
| Mailgun                     | `mailgun`               | [Documentation](/integrations/webhooks/mailgun-webhooks)                                             |
| Microsoft Teams             | `microsoft_teams`       | [Documentation](/integrations/webhooks/teams-webhooks)                                               |
| Modern Treasury             | `modern_treasury`       | [Documentation](/integrations/webhooks/modern-treasury-webhooks)                                     |
| MongoDB                     | `mongodb`               | [Documentation](/integrations/webhooks/mongodb-webhooks)                                             |
| Mux                         | `mux`                   | [Documentation](/integrations/webhooks/mux-webhooks)                                                 |
| Orb                         | `orb`                   | [Documentation](https://developer.withorb.com/docs/orb-docs/webhooks)                                |
| Orbit                       | `orbit`                 | [Documentation](/integrations/webhooks/orbit-webhooks)                                               |
| PagerDuty                   | `pagerduty`             | [Documentation](/integrations/webhooks/pagerduty-webhooks)                                           |
| Pinwheel                    | `pinwheel`              | [Documentation](/integrations/webhooks/pinwheel-webhooks)                                            |
| Plivo                       | `plivo`                 | [Documentation](/integrations/webhooks/plivo-webhooks)                                               |
| Pusher                      | `pusher`                | [Documentation](/integrations/webhooks/pusher-webhooks)                                              |
| SendGrid                    | `sendgrid`              | [Documentation](/integrations/webhooks/sendgrid-webhooks)                                            |
| Sentry                      | `sentry`                | [Documentation](/integrations/webhooks/sentry-webhooks)                                              |
| Shopify                     | `shopify`               | [Documentation](/integrations/webhooks/shopify-webhooks)                                             |
| Signal Sciences             | `signal_sciences`       | [Documentation](/integrations/webhooks/signalsciences-webhooks)                                      |
| Slack                       | `slack`                 | [Documentation](/integrations/webhooks/slack-webhooks)                                               |
| Sonatype Nexus              | `sonatype`              | [Documentation](/integrations/webhooks/sonatype-nexus-webhooks)                                      |
| Square                      | `square`                | [Documentation](/integrations/webhooks/square-webhooks)                                              |
| Stripe                      | `stripe`                | [Documentation](/integrations/webhooks/stripe-webhooks)                                              |
| Svix                        | `svix`                  | [Documentation](/integrations/webhooks/svix-webhooks)                                                |
| Terraform                   | `terraform`             | [Documentation](/integrations/webhooks/terraform-webhooks)                                           |
| TikTok                      | `tiktok`                | [Documentation](/integrations/webhooks/tiktok-webhooks)                                              |
| Trend Micro Conformity      | `trendmicro_conformity` | [Documentation](/integrations/webhooks/trendmicro-webhooks)                                          |
| Twilio                      | `twilio`                | [Documentation](/integrations/webhooks/twilio-webhooks)                                              |
| Twitter                     | `twitter`               | [Documentation](/integrations/webhooks/twitter-webhooks)                                             |
| Typeform                    | `typeform`              | [Documentation](/integrations/webhooks/typeform-webhooks)                                            |
| VMware Workspace            | `vmware`                | [Documentation](/integrations/webhooks/vmware-webhooks)                                              |
| Webex                       | `webex`                 | [Documentation](/integrations/webhooks/webex-webhooks)                                               |
| WhatsApp                    | `whatsapp`              | [Documentation](/integrations/webhooks/whatsapp-webhooks)                                            |
| Worldline                   | `worldline`             | [Documentation](/integrations/webhooks/worldline-webhooks)                                           |
| Xero                        | `xero`                  | [Documentation](/integrations/webhooks/xero-webhooks)                                                |
| Zendesk                     | `zendesk`               | [Documentation](/integrations/webhooks/zendesk-webhooks)                                             |
| Zoom                        | `zoom`                  | [Documentation](/integrations/webhooks/zoom-webhooks)                                                |

## Examples

### Basic example

This example configuration sets up an endpoint (`gitlab-webhook-example.ngrok.app`) that receives webhook requests from GitLab. The **Verify Webhook** action checks the authenticity of the request using a shared secret. If the request is verified, a custom response is sent back with a status `200 OK` and a plain text confirmation message.

#### Example Traffic Policy document

<CodeGroup>
  ```yaml policy.yml theme={null}
  on_http_request:
    - actions:
        - type: verify-webhook
          config:
            provider: gitlab
            secret: secret!
        - type: custom-response
          config:
            status_code: 200
            headers:
              content-type: text/plain
            body: GitLab webhook verified
  ```

  ```json policy.json theme={null}
  {
    "on_http_request": [
      {
        "actions": [
          {
            "type": "verify-webhook",
            "config": {
              "provider": "gitlab",
              "secret": "secret!"
            }
          },
          {
            "type": "custom-response",
            "config": {
              "status_code": 200,
              "headers": {
                "content-type": "text/plain"
              },
              "body": "GitLab webhook verified"
            }
          }
        ]
      }
    ]
  }
  ```
</CodeGroup>

#### Start endpoint with Traffic Policy

```bash  theme={null}
ngrok http 8080 --url gitlab-webhook-example.ngrok.app --traffic-policy-file /path/to/policy.yml
```

```bash  theme={null}
$ curl --location --request POST 'https://gitlab-webhook-example.ngrok.app/' \
--header 'X-Gitlab-Token: secret!'
> POST / HTTP/2
> Host: gitlab-webhook-example.ngrok.app
> User-Agent: curl/[version]
> Accept: */*
> X-Gitlab-Token: secret!
...
```

This request will first be processed by the Verify Webhook action. If the GitLab webhook verification is successful, ngrok will return a `200 OK` response with the message GitLab webhook verified.

```bash  theme={null}
HTTP/2 200 OK
content-type: text/plain
GitLab webhook verified
```

## Action result variables

The following variables are made available for use in subsequent expressions and
CEL interpolations after the action has run. Variable values will only apply
to the last action execution, results are not concatenated.

<ConfigField title="actions.ngrok.verify_webhook.verified" type="bool">
  <p>Indicates whether or not the request was successfully verified.</p>
</ConfigField>

<ConfigField title="actions.ngrok.verify_webhook.error.code" type="string">
  <p>Code for an error that occurred during the invocation of an action.</p>
</ConfigField>

<ConfigField title="actions.ngrok.verify_webhook.error.message" type="string">
  <p>Message for an error that occurred during the invocation of an action.</p>
</ConfigField>


Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Verify Webhook Action

> Validate incoming webhook signatures against a known secret to ensure authenticity.

export const ConfigChildren = ({children}) => {
  return <Accordion title="Show Child Properties">
      {children}
    </Accordion>;
};

export const ConfigField = ({title, type, cel = false, defaultValue = false, required = false, children}) => {
  const id = `config-${title.replace(/\.|\s|\*/g, "_")}`;
  return <div className="field pt-2.5 pb-5 my-2.5 border-gray-50 dark:border-gray-800/50 border-b" style={{
    scrollMarginTop: '120px'
  }} id={id}>
      <div className="flex font-mono group/param-head param-head break-all relative">
        <div className="flex-1 flex content-start py-0.5 mr-5">
          <div className="flex items-center flex-wrap gap-2">
            <div class="absolute -top-1.5">
              <a href={`#${id}`} className="-ml-10 flex items-center opacity-0 border-0 group-hover/param-head:opacity-100 py-2 [.expandable-content_&]:-ml-[2.1rem]" aria-label="Navigate to header">
                ​<div className="w-6 h-6 rounded-md flex items-center justify-center shadow-sm text-gray-400 dark:text-white/50 dark:bg-background-dark dark:brightness-[1.35] dark:ring-1 dark:hover::rightness-150 bg-white ring-1 ring-gray-400/30 dark:ring-gray-700/25 hover:ring-gray-400/60 dark:hover:ring-white/20">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="gray" height="12px" viewBox="0 0 576 512"><path d="M0 256C0 167.6 71.6 96 160 96h72c13.3 0 24 10.7 24 24s-10.7 24-24 24H160C98.1 144 48 194.1 48 256s50.1 112 112 112h72c13.3 0 24 10.7 24 24s-10.7 24-24 24H160C71.6 416 0 344.4 0 256zm576 0c0 88.4-71.6 160-160 160H344c-13.3 0-24-10.7-24-24s10.7-24 24-24h72c61.9 0 112-50.1 112-112s-50.1-112-112-112H344c-13.3 0-24-10.7-24-24s10.7-24 24-24h72c88.4 0 160 71.6 160 160zM184 232H392c13.3 0 24 10.7 24 24s-10.7 24-24 24H184c-13.3 0-24-10.7-24-24s10.7-24 24-24z"></path></svg>
                </div>
              </a>
            </div>
            <div className="font-semibold text-primary dark:text-primary-light overflow-wrap-anywhere">{title}</div>
            <div className="inline items-center gap-2 text-xs font-medium [&_div]:inline [&_div]:mr-2 [&_div]:leading-5 [&_a]:inline [&_a]:mr-2 [&_a]:leading-5">
              {type && <div className="flex items-center px-2 py-0.5 rounded-md bg-gray-100/50 dark:bg-white/5 break-all">
                <span className="text-gray-600 dark:text-gray-200 !font-medium">{type}</span>
              </div>}
              {defaultValue && <div className="flex items-center px-2 py-0.5 rounded-md bg-gray-100/50 dark:bg-white/5 break-all">
                  <span class="text-gray-400 dark:text-gray-500">default:</span>
                  <span className="text-gray-600 dark:text-gray-200 !font-medium">{defaultValue}</span>
                </div>}
              {required && <div className="px-2 py-0.5 rounded-md bg-red-100/50 dark:bg-red-400/10 whitespace-nowrap">
                <span className="text-red-600 dark:text-red-300 !font-medium">Required</span>
              </div>}
              {cel && <a className="px-2 py-0.5 rounded-md !border-none bg-blue-100/50 dark:bg-blue-400/10 whitespace-nowrap" href="/traffic-policy/concepts/cel-interpolation">
                <span className="text-blue-600 dark:text-blue-300 !font-medium">Supports CEL</span>
              </a>}
            </div>
          </div>
        </div>
      </div>
      <div className="mt-4 prose-sm prose-gray dark:prose-invert [&_.prose>p:first-child]:mt-0 [&_.prose>p:last-child]:mb-0">
        {children}
      </div>
    </div>;
};

The **Verify Webhook** Traffic Policy action enables you to validate incoming webhook signatures against a known secret to ensure authenticity. Depending on the verification result, it either forwards the request to the next action or rejects it, safeguarding your endpoints from unauthorized or tampered webhooks.

## Configuration reference

This is the [Traffic Policy](/traffic-policy/) configuration
reference for this action.

### Supported directions

* `on_http_request`

### Type

`verify-webhook`

### Configuration fields

<ConfigField title="provider" type="string" required={true}>
  <p>The name of the provider to verify webhook requests from.</p>
  <p>Value must be a [supported provider](#supported-providers) identifier.</p>
</ConfigField>

<ConfigField title="secret" type="string" required={true} cel={true}>
  <p>The secret key used to validate webhook requests from the specified provider.</p>
  <p>Supports [CEL Interpolation](/traffic-policy/concepts/cel-interpolation).</p>
</ConfigField>

<ConfigField title="enforce" type="bool" required={false}>
  <p>When `true`, the request will be halted if the webhook is not valid and no further actions will run. However when `false`, subsequent actions will run even if the webhook was not valid.</p>
  <p>Default <code>true</code>.</p>
</ConfigField>

## Behavior

The **verify-webhook** action ensures the authenticity of incoming webhook requests by validating their signatures against a known secret. Upon receiving a request, the action performs the signature verification. If verification succeeds, the request proceeds through the action chain. If it fails, the request is terminated with a `403 Forbidden` response, unless `enforce` is set to `false`, in which case the request proceeds without termination.

### Verification process

* **Signature Validation**: The action validates incoming webhook signature to confirm the request originates from the configured provider and that the payload has not been tampered with.
* **Request Handling**: If the webhook verification is successful, the request is forwarded to the next action. If the verification fails, the request chain is terminated with a `403` response.
* **Configurable Enforcement**: By default, verification failures result in termination. However, setting `enforce: false` allows unverified requests to proceed, while logging the verification result. This option is useful for debugging, testing, and crafting your own custom responses with action result variables.

### Endpoint verification

Some webhook providers require an initial endpoint verification challenge to validate that your application is legitimate before sending webhook events. The **verify-webhook** action automatically handles endpoint verification challenges for supported providers.

* Supported providers:
  * Twitter
  * Worldline
  * Xero
  * Zoom

#### Replay prevention with timestamp tolerance

To prevent replay attacks, ngrok verifies that the webhook’s timestamp falls within an acceptable range.

#### Secret handling and encryption

All secrets used for webhook verification are encrypted at config validation. When ngrok processes a requests the secret is decrypted.

### Non-terminating action

This is a **Non-terminating action**. It does not return a response, and will allow Traffic Policy processing to continue to the next Action in the chain. All **Cloud Endpoint** Traffic Policies must end with a terminating action. This requirement does not apply to **Agent Endpoints**.

## Supported providers

Currently, these integration guides refer to modules.

| Provider                    | Provider Identifier     | Integration Guide                                                                                    |
| --------------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------- |
| AfterShip                   | `aftership`             | [Documentation](/integrations/webhooks/aftership-webhooks)                                           |
| Airship                     | `airship`               | [Documentation](/integrations/webhooks/airship-webhooks)                                             |
| Alchemy                     | `alchemy`               | [Documentation](https://docs.alchemy.com/reference/notify-api-quickstart)                            |
| Amazon SNS                  | `sns`                   | [Documentation](/integrations/webhooks/amazon-sns-webhooks)                                          |
| Autodesk Platform Services  | `autodesk`              | [Documentation](/integrations/webhooks/autodesk-webhooks)                                            |
| Bitbucket                   | `bitbucket`             | [Documentation](/integrations/webhooks/bitbucket-webhooks)                                           |
| Bolt                        | `bolt`                  | [Documentation](https://help.bolt.com/developers/guides/webhooks/hook-verification/)                 |
| Box                         | `box`                   | [Documentation](/integrations/webhooks/box-webhooks)                                                 |
| Brex                        | `brex`                  | [Documentation](/integrations/webhooks/brex-webhooks)                                                |
| Buildkite                   | `buildkite`             | [Documentation](/integrations/webhooks/buildkite-webhooks)                                           |
| Calendly                    | `calendly`              | [Documentation](/integrations/webhooks/calendly-webhooks)                                            |
| Castle                      | `castle`                | [Documentation](/integrations/webhooks/castle-webhooks)                                              |
| Chargify                    | `chargify`              | [Documentation](/integrations/webhooks/chargify-webhooks)                                            |
| CircleCI                    | `circleci`              | [Documentation](/integrations/webhooks/circleci-webhooks)                                            |
| Clearbit                    | `clearbit`              | [Documentation](/integrations/webhooks/clearbit-webhooks)                                            |
| Clerk                       | `clerk`                 | [Documentation](/integrations/webhooks/clerk-webhooks)                                               |
| Coinbase                    | `coinbase`              | [Documentation](/integrations/webhooks/coinbase-webhooks)                                            |
| Contentful                  | `contentful`            | [Documentation](/integrations/webhooks/contentful-webhooks)                                          |
| DocuSign                    | `docusign`              | [Documentation](/integrations/webhooks/docusign-webhooks)                                            |
| Dropbox                     | `dropbox`               | [Documentation](/integrations/webhooks/dropbox-webhooks)                                             |
| Facebook Graph API          | `facebook_graph_api`    | [Documentation](/integrations/webhooks/facebook-webhooks)                                            |
| Facebook Messenger          | `facebook_messenger`    | [Documentation](/integrations/webhooks/facebook-messenger-webhooks)                                  |
| Frame.io                    | `frameio`               | [Documentation](/integrations/webhooks/frameio-webhooks)                                             |
| GitHub                      | `github`                | [Documentation](/integrations/webhooks/github-webhooks)                                              |
| GitLab                      | `gitlab`                | [Documentation](/integrations/webhooks/gitlab-webhooks)                                              |
| Go1                         | `go1`                   | [Documentation](https://www.go1.com/developers/partners/concepts/webhook-signature-authentification) |
| Heroku                      | `heroku`                | [Documentation](/integrations/webhooks/heroku-webhooks)                                              |
| Hosted Hooks                | `hostedhooks`           | [Documentation](/integrations/webhooks/hostedhooks-webhooks)                                         |
| HubSpot                     | `hubspot`               | [Documentation](/integrations/webhooks/hubspot-webhooks)                                             |
| Hygraph (Formerly GraphCMS) | `graphcms`              | [Documentation](/integrations/webhooks/hygraph-webhooks)                                             |
| Instagram                   | `instagram`             | [Documentation](/integrations/webhooks/instagram-webhooks)                                           |
| Intercom                    | `intercom`              | [Documentation](/integrations/webhooks/intercom-webhooks)                                            |
| Jira                        | `jira`                  | [Documentation](/integrations/webhooks/jira-webhooks)                                                |
| Launch Darkly               | `launch_darkly`         | [Documentation](/integrations/webhooks/launchdarkly-webhooks)                                        |
| Linear                      | `linear`                | [Documentation](/integrations/webhooks/linear-webhooks)                                              |
| Mailchimp                   | `mailchimp`             | [Documentation](/integrations/webhooks/mailchimp-webhooks)                                           |
| Mailgun                     | `mailgun`               | [Documentation](/integrations/webhooks/mailgun-webhooks)                                             |
| Microsoft Teams             | `microsoft_teams`       | [Documentation](/integrations/webhooks/teams-webhooks)                                               |
| Modern Treasury             | `modern_treasury`       | [Documentation](/integrations/webhooks/modern-treasury-webhooks)                                     |
| MongoDB                     | `mongodb`               | [Documentation](/integrations/webhooks/mongodb-webhooks)                                             |
| Mux                         | `mux`                   | [Documentation](/integrations/webhooks/mux-webhooks)                                                 |
| Orb                         | `orb`                   | [Documentation](https://developer.withorb.com/docs/orb-docs/webhooks)                                |
| Orbit                       | `orbit`                 | [Documentation](/integrations/webhooks/orbit-webhooks)                                               |
| PagerDuty                   | `pagerduty`             | [Documentation](/integrations/webhooks/pagerduty-webhooks)                                           |
| Pinwheel                    | `pinwheel`              | [Documentation](/integrations/webhooks/pinwheel-webhooks)                                            |
| Plivo                       | `plivo`                 | [Documentation](/integrations/webhooks/plivo-webhooks)                                               |
| Pusher                      | `pusher`                | [Documentation](/integrations/webhooks/pusher-webhooks)                                              |
| SendGrid                    | `sendgrid`              | [Documentation](/integrations/webhooks/sendgrid-webhooks)                                            |
| Sentry                      | `sentry`                | [Documentation](/integrations/webhooks/sentry-webhooks)                                              |
| Shopify                     | `shopify`               | [Documentation](/integrations/webhooks/shopify-webhooks)                                             |
| Signal Sciences             | `signal_sciences`       | [Documentation](/integrations/webhooks/signalsciences-webhooks)                                      |
| Slack                       | `slack`                 | [Documentation](/integrations/webhooks/slack-webhooks)                                               |
| Sonatype Nexus              | `sonatype`              | [Documentation](/integrations/webhooks/sonatype-nexus-webhooks)                                      |
| Square                      | `square`                | [Documentation](/integrations/webhooks/square-webhooks)                                              |
| Stripe                      | `stripe`                | [Documentation](/integrations/webhooks/stripe-webhooks)                                              |
| Svix                        | `svix`                  | [Documentation](/integrations/webhooks/svix-webhooks)                                                |
| Terraform                   | `terraform`             | [Documentation](/integrations/webhooks/terraform-webhooks)                                           |
| TikTok                      | `tiktok`                | [Documentation](/integrations/webhooks/tiktok-webhooks)                                              |
| Trend Micro Conformity      | `trendmicro_conformity` | [Documentation](/integrations/webhooks/trendmicro-webhooks)                                          |
| Twilio                      | `twilio`                | [Documentation](/integrations/webhooks/twilio-webhooks)                                              |
| Twitter                     | `twitter`               | [Documentation](/integrations/webhooks/twitter-webhooks)                                             |
| Typeform                    | `typeform`              | [Documentation](/integrations/webhooks/typeform-webhooks)                                            |
| VMware Workspace            | `vmware`                | [Documentation](/integrations/webhooks/vmware-webhooks)                                              |
| Webex                       | `webex`                 | [Documentation](/integrations/webhooks/webex-webhooks)                                               |
| WhatsApp                    | `whatsapp`              | [Documentation](/integrations/webhooks/whatsapp-webhooks)                                            |
| Worldline                   | `worldline`             | [Documentation](/integrations/webhooks/worldline-webhooks)                                           |
| Xero                        | `xero`                  | [Documentation](/integrations/webhooks/xero-webhooks)                                                |
| Zendesk                     | `zendesk`               | [Documentation](/integrations/webhooks/zendesk-webhooks)                                             |
| Zoom                        | `zoom`                  | [Documentation](/integrations/webhooks/zoom-webhooks)                                                |

## Examples

### Basic example

This example configuration sets up an endpoint (`gitlab-webhook-example.ngrok.app`) that receives webhook requests from GitLab. The **Verify Webhook** action checks the authenticity of the request using a shared secret. If the request is verified, a custom response is sent back with a status `200 OK` and a plain text confirmation message.

#### Example Traffic Policy document

<CodeGroup>
  ```yaml policy.yml theme={null}
  on_http_request:
    - actions:
        - type: verify-webhook
          config:
            provider: gitlab
            secret: secret!
        - type: custom-response
          config:
            status_code: 200
            headers:
              content-type: text/plain
            body: GitLab webhook verified
  ```

  ```json policy.json theme={null}
  {
    "on_http_request": [
      {
        "actions": [
          {
            "type": "verify-webhook",
            "config": {
              "provider": "gitlab",
              "secret": "secret!"
            }
          },
          {
            "type": "custom-response",
            "config": {
              "status_code": 200,
              "headers": {
                "content-type": "text/plain"
              },
              "body": "GitLab webhook verified"
            }
          }
        ]
      }
    ]
  }
  ```
</CodeGroup>

#### Start endpoint with Traffic Policy

```bash  theme={null}
ngrok http 8080 --url gitlab-webhook-example.ngrok.app --traffic-policy-file /path/to/policy.yml
```

```bash  theme={null}
$ curl --location --request POST 'https://gitlab-webhook-example.ngrok.app/' \
--header 'X-Gitlab-Token: secret!'
> POST / HTTP/2
> Host: gitlab-webhook-example.ngrok.app
> User-Agent: curl/[version]
> Accept: */*
> X-Gitlab-Token: secret!
...
```

This request will first be processed by the Verify Webhook action. If the GitLab webhook verification is successful, ngrok will return a `200 OK` response with the message GitLab webhook verified.

```bash  theme={null}
HTTP/2 200 OK
content-type: text/plain
GitLab webhook verified
```

## Action result variables

The following variables are made available for use in subsequent expressions and
CEL interpolations after the action has run. Variable values will only apply
to the last action execution, results are not concatenated.

<ConfigField title="actions.ngrok.verify_webhook.verified" type="bool">
  <p>Indicates whether or not the request was successfully verified.</p>
</ConfigField>

<ConfigField title="actions.ngrok.verify_webhook.error.code" type="string">
  <p>Code for an error that occurred during the invocation of an action.</p>
</ConfigField>

<ConfigField title="actions.ngrok.verify_webhook.error.message" type="string">
  <p>Message for an error that occurred during the invocation of an action.</p>
</ConfigField>


Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# API Filtering

> Learn how to use API Filtering to make operational tooling faster and more precise.

When using ngrok's API, you can add the `filter` query parameter to `GET` requests to return only those results which match a provided criteria. This makes automated management of resources easier while eliminating the need to download large collections and filter client-side.

To use API Filtering, you pass a subset of CEL expressions to the `filter` query parameter, as demonstrated in the following example.

This example request fetches a list of all your Cloud and Agent endpoints.

```http  theme={null}
GET /endpoints?filter=obj.type == "cloud" || obj.type == "agent"
```

## Request shape

```http  theme={null}
GET /{resource}?filter={CEL_EXPRESSION}
```

### cURL usage

```
curl --location 'https://api.ngrok.com/endpoints' \
  --get \
  --data-urlencode '<filter>' \
  --header 'Ngrok-Version: 2' \
  --header 'Authorization: Bearer <token>'
```

## Supported CEL (subset)

These core operators and helpers are supported:

* Logical operators: `!`, `&&`, `||`
* Comparative operators: `<`, `<=`, `==`, `!=`, `>=`, `>`
* Parentheses for grouping
* List membership using the `in` keyword
* \[Coming soon] String substring checks: `startsWith()`, `contains()`, `endsWith()`
* Length / emptiness checks: `size()`, `== ""`, `== null`
* Date and time helpers: `timestamp(RFC-3339)`, `timestamp(time.now)`, `timestamp(time.now).subtract(<duration>)`, `timestamp(time.now).add(<duration>)`

### Instance inspection (versus list comprehension)

Expressions are evaluated against a single **resource instance** exposed as `obj`. Compare fields **on the instance** rather than attempting list-wise checks on fields.

✅ Valid

```http  theme={null}
GET /endpoints?filter=obj.type == "cloud" || obj.type == "agent"
GET /endpoints?filter=obj.type in ["agent", "cloud"]
GET /endpoints?filter="public" in obj.bindings || "internal" in obj.bindings
```

❌ Not valid

```http  theme={null}
GET /endpoints?filter=["agent","cloud"] in obj.types
GET /endpoints?filter=obj.bindings in ["public", "internal"]
```

## Dates and time helpers

* **Treat timestamps as numerics** by using `<`, `<=`, `==`, `>=`, `>` directly on `timestamp()` fields, for example:
  ```http  theme={null}
  GET /vaults?filter=obj.created_at < timestamp("2025-10-31T09:23:45-07:00")
  ```
* **Relative helpers based on the current time:** Use `timestamp(time.now)` for the current time, then chain `.subtract(<duration>)` or `.add(<duration>)` with a duration string such as `"7d"`, `"24h"`, or `"15m"`. For example:
  ```http  theme={null}
  # resources created in the last 7 days
  GET /endpoints?filter=obj.created_at >= timestamp(time.now).subtract("7d")

  # resources that will expire within the next 24 hours
  GET /tls_certificates?filter=obj.not_after <= timestamp(time.now).add("24h")
  ```

## Query restrictions and limitations

### Unsupported CEL features

To keep filter evaluation small and predictable, the following CEL features are not supported.

* **No index access** (for example, `a[0]`)
* **No arithmetic** (for example, `a + b`)
* **No ternary** (for example, `cond ? x : y`)
* **No type checks** (for example, `type(a) == string`)
* **No regexes**
* **No fuzzy matching**

These exclusions intentionally keep evaluation small and predictable.

### High-entropy fields and substring checks

**High entropy** fields are fields with values that are effectively random, usually because they're generated. The `id` field on a response object, such as `obj.id`, is a common example.

[Substring functions](https://github.com/google/cel-spec/blob/master/doc/langdef.md#string-functions), such as `startsWith()`, `contains()`, and `endsWith()`, are **disallowed** on high entropy fields. Check for equality on these fields instead. For example:

```
obj.id == "ep_123"
```

### Query complexity (budgeting/limits)

Very large expressions can stress the query engine. The service may enforce **limits on the number of conditions per query** or similar throttles in the future.

## Filterable resources and fields

The initial release prioritizes the resource types and fields below. CEL filtering is not supported on deprecated endpoints. Field coverage is evolving and may change before GA.

| Resource Type                   | Filterable Fields                                                                                                                                                                                          |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Endpoints**                   | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`<br />- `principal.id`<br />- `type`<br />- `binding`<br />- `url`<br />- `pooling_enabled`<br />- `scheme`<br />- `region`<br />- `name` |
| **Reserved Addresses**          | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`<br />- `addr`<br />- `region`                                                                                                            |
| **Reserved Domains**            | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`<br />- `domain`<br />- `region`<br />- `cname_target`<br />- `certificate.id`<br />- `acme_challenge_cname_target`                       |
| **TLS Certificates**            | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`<br />- `subject_common_name`<br />- `not_after`<br />- `not_before`<br />- `serial_number`                                               |
| **Certificate Authorities**     | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`<br />- `subject_common_name`<br />- `not_before`<br />- `not_after`                                                                      |
| **IP Policies**                 | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`                                                                                                                                          |
| **IP Policy Rules**             | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`<br />- `ip_policy`<br />- `cidr`<br />- `action`                                                                                         |
| **Agent Ingress**               | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`<br />- `domain`                                                                                                                          |
| **Tunnel Sessions**             | - `id`<br />- `metadata`<br />- `agent_version`<br />- `ip`<br />- `os`<br />- `region`<br />- `started_at`<br />- `credential`                                                                            |
| **Event Destinations**          | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`                                                                                                                                          |
| **Event Subscriptions**         | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`                                                                                                                                          |
| **IP Restrictions**             | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`                                                                                                                                          |
| **API Keys**                    | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`<br />- `owner_id`                                                                                                                        |
| **SSH Credentials**             | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`<br />- `owner_id`<br />- `acl`                                                                                                           |
| **Credentials**                 | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`<br />- `owner_id`<br />- `acl`                                                                                                           |
| **Service Users**               | - `id`<br />- `created_at`                                                                                                                                                                                 |
| **SSH Certificate Authorities** | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`                                                                                                                                          |
| **Vaults**                      | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`<br />- `name`                                                                                                                            |
| **Secrets**                     | - `id`<br />- `created_at`<br />- `description`<br />- `metadata`<br />- `name`                                                                                                                            |

## Usage examples

### **Filter endpoints by type and creation time**

```http  theme={null}
GET /endpoints?filter=obj.type == "cloud" && obj.created_at < timestamp("2025-10-31T09:23:45-07:00")
# or using helpers
GET /endpoints?filter=obj.type == "cloud" && obj.created_at >= timestamp(time.now).subtract("6d")
```

Reference:

* [`LIST /endpoints`](/api-reference/endpoints/list)

### **Reserved domains by prefix**

```http  theme={null}
GET /reserved_domains?filter=obj.domain.startsWith("myapi.ngrok")
```

Reference:

* [`LIST /reserved_domains`](/api-reference/reserveddomains/list)

### **IP policy rules by CIDR and action**

```http  theme={null}
GET /ip_policy_rules?filter=obj.cidr.contains("1.1.0.0/16") && obj.action == "deny"
```

Reference:

* [`LIST /ip_policy_rules`](/api-reference/ippolicyrules/list)

### **Credentials by owner with optional empty ACL**

```http  theme={null}
GET /credentials?filter=obj.owner_id == "usr_2tEpN0yrxDI4j8jVnhVRoTNN2Tx" && (obj.acl == null || obj.acl == "")
```

Reference:

* [`LIST /credentials`](/api-reference/credentials/list)

### **Complex nesting**

```http  theme={null}
GET /agent_ingresses?filter=obj.domain in ["foo.com","bar.com","baz.com"] || (obj.created_at < timestamp("2025-05-10Z") && obj.description.contains("cowbell"))
```

Reference:

* [`LIST /agent_ingresses`](/api-reference/agentingresses/list)

## Error handling

Invalid filters return **HTTP 400** with a structured error body (`category`, `status_code`, `message`, `details`). Example:

```http  theme={null}
HTTP/1.1 400 Bad Request
Content-Type: application/json; charset=utf-8
Cache-Control: no-store

{
  "error_code": "invalid_cel_expression",
  "status_code": 400,
  "msg": "Invalid CEL query: unsupported field: endpoint.idk (must be endpoint.url, endpoint.id, endpoint.type, or endpoint.bindings).",
  "details": {
    "operation_id": "op_k23j45n134jkasdfk34jkjnlkjuhasdf"
  }
}
```


Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> List all agent endpoint configurations in your ngrok account with optional filtering and pagination.

# List



## OpenAPI

````yaml get /endpoints
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /endpoints:
    get:
      tags:
        - Endpoints
      summary: List
      description: |
        List all active endpoints on the account
      operationId: EndpointsList
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: before_id
          description: >
            Expects a resource ID as its input. Returns earlier entries in the
            result set, sorted by ID.
          in: query
          required: false
          schema:
            type: string
        - name: limit
          description: >
            Constrains the number of results in the dataset. See the [API
            Overview](https://ngrok.com/docs/api/index#pagination) for details.
          in: query
          required: false
          schema:
            type: string
        - name: id
          description: |
            Filter results by endpoint IDs. Deprecated: use `filter` instead.
          in: query
          required: false
          schema:
            type: array
        - name: url
          description: |
            Filter results by endpoint URLs. Deprecated: use `filter` instead.
          in: query
          required: false
          schema:
            type: array
        - name: filter
          description: >
            A CEL expression to filter the list results. Supports logical and
            comparison operators to match on fields such as `id`, `metadata`,
            `created_at`, and more. See ngrok API Filtering for syntax and field
            details: https://ngrok.com/docs/api/api-filtering.
          in: query
          required: false
          schema:
            type: string
      responses:
        '200':
          description: |
            List all active endpoints on the account
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EndpointList'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    EndpointList:
      type: object
      properties:
        endpoints:
          description: |
            the list of all active endpoints on this account
          type: array
          items:
            $ref: '#/components/schemas/Endpoint'
        uri:
          description: |
            URI of the endpoints list API resource
          type: string
        next_page_uri:
          description: |
            URI of the next page, or null if there is no next page
          type: string
    Endpoint:
      type: object
      properties:
        id:
          description: |
            unique endpoint resource identifier
          type: string
        region:
          description: |
            identifier of the region this endpoint belongs to
          type: string
        created_at:
          description: |
            timestamp when the endpoint was created in RFC 3339 format
          type: string
        updated_at:
          description: |
            timestamp when the endpoint was updated in RFC 3339 format
          type: string
        public_url:
          description: >
            deprecated [replaced by URL]: URL of the hostport served by this
            endpoint
          type: string
        proto:
          description: >
            protocol served by this endpoint. one of `http`, `https`, `tcp`, or
            `tls`
          type: string
        scheme:
          description: n/a
          type: string
        hostport:
          description: >
            hostport served by this endpoint (hostname:port) -> soon to be
            deprecated
          type: string
        host:
          description: n/a
          type: string
        port:
          description: n/a
          type: integer
        type:
          description: >
            whether the endpoint is `ephemeral` (served directly by an
            agent-initiated tunnel) or `edge` (served by an edge) or `cloud
            (represents a cloud endpoint)`
          type: string
        metadata:
          description: |
            user-supplied metadata of the associated tunnel or edge object
          type: string
        description:
          description: |
            user-supplied description of the associated tunnel
          type: string
        domain:
          $ref: '#/components/schemas/Ref'
          description: |
            the domain reserved for this endpoint
        tcp_addr:
          $ref: '#/components/schemas/Ref'
          description: |
            the address reserved for this endpoint
        tunnel:
          $ref: '#/components/schemas/Ref'
          description: >
            the tunnel serving requests to this endpoint, if this is an
            ephemeral endpoint
        edge:
          $ref: '#/components/schemas/Ref'
          description: >
            the edge serving requests to this endpoint, if this is an edge
            endpoint
        upstream_url:
          description: |
            the local address the tunnel forwards to
          type: string
        upstream_protocol:
          description: |
            the protocol the agent uses to forward with
          type: string
        url:
          description: |
            the url of the endpoint
          type: string
        principal:
          $ref: '#/components/schemas/Ref'
          description: |
            The ID of the owner (bot or user) that owns this endpoint
        traffic_policy:
          description: |
            The traffic policy attached to this endpoint
          type: string
        bindings:
          description: |
            the bindings associated with this endpoint
          type: array
          items:
            type: string
        tunnel_session:
          $ref: '#/components/schemas/Ref'
          description: |
            The tunnel session of the agent for this endpoint
        uri:
          description: |
            URI of the Cloud Endpoint API resource
          type: string
        name:
          description: |
            user supplied name for the endpoint
          type: string
        pooling_enabled:
          description: |
            whether the endpoint allows pooling
          type: boolean
    Ref:
      type: object
      properties:
        id:
          description: |
            a resource identifier
          type: string
        uri:
          description: |
            a uri for locating a resource
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> List all agent endpoint configurations in your ngrok account with optional filtering and pagination.

# List



## OpenAPI

````yaml get /endpoints
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /endpoints:
    get:
      tags:
        - Endpoints
      summary: List
      description: |
        List all active endpoints on the account
      operationId: EndpointsList
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: before_id
          description: >
            Expects a resource ID as its input. Returns earlier entries in the
            result set, sorted by ID.
          in: query
          required: false
          schema:
            type: string
        - name: limit
          description: >
            Constrains the number of results in the dataset. See the [API
            Overview](https://ngrok.com/docs/api/index#pagination) for details.
          in: query
          required: false
          schema:
            type: string
        - name: id
          description: |
            Filter results by endpoint IDs. Deprecated: use `filter` instead.
          in: query
          required: false
          schema:
            type: array
        - name: url
          description: |
            Filter results by endpoint URLs. Deprecated: use `filter` instead.
          in: query
          required: false
          schema:
            type: array
        - name: filter
          description: >
            A CEL expression to filter the list results. Supports logical and
            comparison operators to match on fields such as `id`, `metadata`,
            `created_at`, and more. See ngrok API Filtering for syntax and field
            details: https://ngrok.com/docs/api/api-filtering.
          in: query
          required: false
          schema:
            type: string
      responses:
        '200':
          description: |
            List all active endpoints on the account
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EndpointList'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    EndpointList:
      type: object
      properties:
        endpoints:
          description: |
            the list of all active endpoints on this account
          type: array
          items:
            $ref: '#/components/schemas/Endpoint'
        uri:
          description: |
            URI of the endpoints list API resource
          type: string
        next_page_uri:
          description: |
            URI of the next page, or null if there is no next page
          type: string
    Endpoint:
      type: object
      properties:
        id:
          description: |
            unique endpoint resource identifier
          type: string
        region:
          description: |
            identifier of the region this endpoint belongs to
          type: string
        created_at:
          description: |
            timestamp when the endpoint was created in RFC 3339 format
          type: string
        updated_at:
          description: |
            timestamp when the endpoint was updated in RFC 3339 format
          type: string
        public_url:
          description: >
            deprecated [replaced by URL]: URL of the hostport served by this
            endpoint
          type: string
        proto:
          description: >
            protocol served by this endpoint. one of `http`, `https`, `tcp`, or
            `tls`
          type: string
        scheme:
          description: n/a
          type: string
        hostport:
          description: >
            hostport served by this endpoint (hostname:port) -> soon to be
            deprecated
          type: string
        host:
          description: n/a
          type: string
        port:
          description: n/a
          type: integer
        type:
          description: >
            whether the endpoint is `ephemeral` (served directly by an
            agent-initiated tunnel) or `edge` (served by an edge) or `cloud
            (represents a cloud endpoint)`
          type: string
        metadata:
          description: |
            user-supplied metadata of the associated tunnel or edge object
          type: string
        description:
          description: |
            user-supplied description of the associated tunnel
          type: string
        domain:
          $ref: '#/components/schemas/Ref'
          description: |
            the domain reserved for this endpoint
        tcp_addr:
          $ref: '#/components/schemas/Ref'
          description: |
            the address reserved for this endpoint
        tunnel:
          $ref: '#/components/schemas/Ref'
          description: >
            the tunnel serving requests to this endpoint, if this is an
            ephemeral endpoint
        edge:
          $ref: '#/components/schemas/Ref'
          description: >
            the edge serving requests to this endpoint, if this is an edge
            endpoint
        upstream_url:
          description: |
            the local address the tunnel forwards to
          type: string
        upstream_protocol:
          description: |
            the protocol the agent uses to forward with
          type: string
        url:
          description: |
            the url of the endpoint
          type: string
        principal:
          $ref: '#/components/schemas/Ref'
          description: |
            The ID of the owner (bot or user) that owns this endpoint
        traffic_policy:
          description: |
            The traffic policy attached to this endpoint
          type: string
        bindings:
          description: |
            the bindings associated with this endpoint
          type: array
          items:
            type: string
        tunnel_session:
          $ref: '#/components/schemas/Ref'
          description: |
            The tunnel session of the agent for this endpoint
        uri:
          description: |
            URI of the Cloud Endpoint API resource
          type: string
        name:
          description: |
            user supplied name for the endpoint
          type: string
        pooling_enabled:
          description: |
            whether the endpoint allows pooling
          type: boolean
    Ref:
      type: object
      properties:
        id:
          description: |
            a resource identifier
          type: string
        uri:
          description: |
            a uri for locating a resource
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> List all agent endpoint configurations in your ngrok account with optional filtering and pagination.

# List



## OpenAPI

````yaml get /endpoints
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /endpoints:
    get:
      tags:
        - Endpoints
      summary: List
      description: |
        List all active endpoints on the account
      operationId: EndpointsList
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: before_id
          description: >
            Expects a resource ID as its input. Returns earlier entries in the
            result set, sorted by ID.
          in: query
          required: false
          schema:
            type: string
        - name: limit
          description: >
            Constrains the number of results in the dataset. See the [API
            Overview](https://ngrok.com/docs/api/index#pagination) for details.
          in: query
          required: false
          schema:
            type: string
        - name: id
          description: |
            Filter results by endpoint IDs. Deprecated: use `filter` instead.
          in: query
          required: false
          schema:
            type: array
        - name: url
          description: |
            Filter results by endpoint URLs. Deprecated: use `filter` instead.
          in: query
          required: false
          schema:
            type: array
        - name: filter
          description: >
            A CEL expression to filter the list results. Supports logical and
            comparison operators to match on fields such as `id`, `metadata`,
            `created_at`, and more. See ngrok API Filtering for syntax and field
            details: https://ngrok.com/docs/api/api-filtering.
          in: query
          required: false
          schema:
            type: string
      responses:
        '200':
          description: |
            List all active endpoints on the account
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EndpointList'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    EndpointList:
      type: object
      properties:
        endpoints:
          description: |
            the list of all active endpoints on this account
          type: array
          items:
            $ref: '#/components/schemas/Endpoint'
        uri:
          description: |
            URI of the endpoints list API resource
          type: string
        next_page_uri:
          description: |
            URI of the next page, or null if there is no next page
          type: string
    Endpoint:
      type: object
      properties:
        id:
          description: |
            unique endpoint resource identifier
          type: string
        region:
          description: |
            identifier of the region this endpoint belongs to
          type: string
        created_at:
          description: |
            timestamp when the endpoint was created in RFC 3339 format
          type: string
        updated_at:
          description: |
            timestamp when the endpoint was updated in RFC 3339 format
          type: string
        public_url:
          description: >
            deprecated [replaced by URL]: URL of the hostport served by this
            endpoint
          type: string
        proto:
          description: >
            protocol served by this endpoint. one of `http`, `https`, `tcp`, or
            `tls`
          type: string
        scheme:
          description: n/a
          type: string
        hostport:
          description: >
            hostport served by this endpoint (hostname:port) -> soon to be
            deprecated
          type: string
        host:
          description: n/a
          type: string
        port:
          description: n/a
          type: integer
        type:
          description: >
            whether the endpoint is `ephemeral` (served directly by an
            agent-initiated tunnel) or `edge` (served by an edge) or `cloud
            (represents a cloud endpoint)`
          type: string
        metadata:
          description: |
            user-supplied metadata of the associated tunnel or edge object
          type: string
        description:
          description: |
            user-supplied description of the associated tunnel
          type: string
        domain:
          $ref: '#/components/schemas/Ref'
          description: |
            the domain reserved for this endpoint
        tcp_addr:
          $ref: '#/components/schemas/Ref'
          description: |
            the address reserved for this endpoint
        tunnel:
          $ref: '#/components/schemas/Ref'
          description: >
            the tunnel serving requests to this endpoint, if this is an
            ephemeral endpoint
        edge:
          $ref: '#/components/schemas/Ref'
          description: >
            the edge serving requests to this endpoint, if this is an edge
            endpoint
        upstream_url:
          description: |
            the local address the tunnel forwards to
          type: string
        upstream_protocol:
          description: |
            the protocol the agent uses to forward with
          type: string
        url:
          description: |
            the url of the endpoint
          type: string
        principal:
          $ref: '#/components/schemas/Ref'
          description: |
            The ID of the owner (bot or user) that owns this endpoint
        traffic_policy:
          description: |
            The traffic policy attached to this endpoint
          type: string
        bindings:
          description: |
            the bindings associated with this endpoint
          type: array
          items:
            type: string
        tunnel_session:
          $ref: '#/components/schemas/Ref'
          description: |
            The tunnel session of the agent for this endpoint
        uri:
          description: |
            URI of the Cloud Endpoint API resource
          type: string
        name:
          description: |
            user supplied name for the endpoint
          type: string
        pooling_enabled:
          description: |
            whether the endpoint allows pooling
          type: boolean
    Ref:
      type: object
      properties:
        id:
          description: |
            a resource identifier
          type: string
        uri:
          description: |
            a uri for locating a resource
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Delete a specific agent endpoint configuration by its unique identifier.

# Delete



## OpenAPI

````yaml delete /endpoints/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /endpoints/{id}:
    delete:
      tags:
        - Endpoints
      summary: Delete
      description: |
        Delete an Endpoint by ID, currently available only for cloud endpoints
      operationId: EndpointsDelete
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            a resource identifier
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: >
            Delete an Endpoint by ID, currently available only for cloud
            endpoints
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Delete a specific agent endpoint configuration by its unique identifier.

# Delete



## OpenAPI

````yaml delete /endpoints/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /endpoints/{id}:
    delete:
      tags:
        - Endpoints
      summary: Delete
      description: |
        Delete an Endpoint by ID, currently available only for cloud endpoints
      operationId: EndpointsDelete
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            a resource identifier
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: >
            Delete an Endpoint by ID, currently available only for cloud
            endpoints
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> List all reserved static IP addresses in your ngrok account with optional filtering.

# List



## OpenAPI

````yaml get /reserved_addrs
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /reserved_addrs:
    get:
      tags:
        - ReservedAddrs
      summary: List
      description: |
        List all reserved addresses on this account.
      operationId: ReservedAddrsList
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: before_id
          description: >
            Expects a resource ID as its input. Returns earlier entries in the
            result set, sorted by ID.
          in: query
          required: false
          schema:
            type: string
        - name: limit
          description: >
            Constrains the number of results in the dataset. See the [API
            Overview](https://ngrok.com/docs/api/index#pagination) for details.
          in: query
          required: false
          schema:
            type: string
        - name: filter
          description: >
            A CEL expression to filter the list results. Supports logical and
            comparison operators to match on fields such as `id`, `metadata`,
            `created_at`, and more. See ngrok API Filtering for syntax and field
            details: https://ngrok.com/docs/api/api-filtering.
          in: query
          required: false
          schema:
            type: string
      responses:
        '200':
          description: |
            List all reserved addresses on this account.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReservedAddrList'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    ReservedAddrList:
      type: object
      properties:
        reserved_addrs:
          description: |
            the list of all reserved addresses on this account
          type: array
          items:
            $ref: '#/components/schemas/ReservedAddr'
        uri:
          description: |
            URI of the reserved address list API resource
          type: string
        next_page_uri:
          description: |
            URI of the next page, or null if there is no next page
          type: string
    ReservedAddr:
      type: object
      properties:
        id:
          description: |
            unique reserved address resource identifier
          type: string
        uri:
          description: |
            URI of the reserved address API resource
          type: string
        created_at:
          description: |
            timestamp when the reserved address was created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
        addr:
          description: >
            hostname:port of the reserved address that was assigned at creation
            time
          type: string
        region:
          description: >
            reserve the address in this geographic ngrok datacenter. Optional,
            default is us. (au, eu, ap, us, jp, in, sa)
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Reserve a static IP address for use with your ngrok endpoints and edges.

# Create



## OpenAPI

````yaml post /reserved_addrs
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /reserved_addrs:
    post:
      tags:
        - ReservedAddrs
      summary: Create
      description: |
        Create a new reserved address.
      operationId: ReservedAddrsCreate
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ReservedAddrCreate'
      responses:
        '201':
          description: |
            Create a new reserved address.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReservedAddr'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    ReservedAddrCreate:
      type: object
      properties:
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
        region:
          description: >
            reserve the address in this geographic ngrok datacenter. Optional,
            default is us. (au, eu, ap, us, jp, in, sa)
          type: string
    ReservedAddr:
      type: object
      properties:
        id:
          description: |
            unique reserved address resource identifier
          type: string
        uri:
          description: |
            URI of the reserved address API resource
          type: string
        created_at:
          description: |
            timestamp when the reserved address was created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
        addr:
          description: >
            hostname:port of the reserved address that was assigned at creation
            time
          type: string
        region:
          description: >
            reserve the address in this geographic ngrok datacenter. Optional,
            default is us. (au, eu, ap, us, jp, in, sa)
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Retrieve details about a specific reserved static IP address including its status and usage.

# Get



## OpenAPI

````yaml get /reserved_addrs/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /reserved_addrs/{id}:
    get:
      tags:
        - ReservedAddrs
      summary: Get
      description: |
        Get the details of a reserved address.
      operationId: ReservedAddrsGet
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            a resource identifier
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: |
            Get the details of a reserved address.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReservedAddr'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    ReservedAddr:
      type: object
      properties:
        id:
          description: |
            unique reserved address resource identifier
          type: string
        uri:
          description: |
            URI of the reserved address API resource
          type: string
        created_at:
          description: |
            timestamp when the reserved address was created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
        addr:
          description: >
            hostname:port of the reserved address that was assigned at creation
            time
          type: string
        region:
          description: >
            reserve the address in this geographic ngrok datacenter. Optional,
            default is us. (au, eu, ap, us, jp, in, sa)
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Release a reserved static IP address by its unique identifier.

# Delete



## OpenAPI

````yaml delete /reserved_addrs/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /reserved_addrs/{id}:
    delete:
      tags:
        - ReservedAddrs
      summary: Delete
      description: |
        Delete a reserved address.
      operationId: ReservedAddrsDelete
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            a resource identifier
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: |
            Delete a reserved address.
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Update an existing reserved static IP address configuration or metadata.

# Update



## OpenAPI

````yaml patch /reserved_addrs/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /reserved_addrs/{id}:
    patch:
      tags:
        - ReservedAddrs
      summary: Update
      description: |
        Update the attributes of a reserved address.
      operationId: ReservedAddrsUpdate
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ReservedAddrUpdate'
      responses:
        '200':
          description: |
            Update the attributes of a reserved address.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReservedAddr'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    ReservedAddrUpdate:
      type: object
      properties:
        id:
          description: n/a
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
    ReservedAddr:
      type: object
      properties:
        id:
          description: |
            unique reserved address resource identifier
          type: string
        uri:
          description: |
            URI of the reserved address API resource
          type: string
        created_at:
          description: |
            timestamp when the reserved address was created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
        addr:
          description: >
            hostname:port of the reserved address that was assigned at creation
            time
          type: string
        region:
          description: >
            reserve the address in this geographic ngrok datacenter. Optional,
            default is us. (au, eu, ap, us, jp, in, sa)
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Update an existing reserved static IP address configuration or metadata.

# Update



## OpenAPI

````yaml patch /reserved_addrs/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /reserved_addrs/{id}:
    patch:
      tags:
        - ReservedAddrs
      summary: Update
      description: |
        Update the attributes of a reserved address.
      operationId: ReservedAddrsUpdate
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ReservedAddrUpdate'
      responses:
        '200':
          description: |
            Update the attributes of a reserved address.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReservedAddr'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    ReservedAddrUpdate:
      type: object
      properties:
        id:
          description: n/a
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
    ReservedAddr:
      type: object
      properties:
        id:
          description: |
            unique reserved address resource identifier
          type: string
        uri:
          description: |
            URI of the reserved address API resource
          type: string
        created_at:
          description: |
            timestamp when the reserved address was created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
        addr:
          description: >
            hostname:port of the reserved address that was assigned at creation
            time
          type: string
        region:
          description: >
            reserve the address in this geographic ngrok datacenter. Optional,
            default is us. (au, eu, ap, us, jp, in, sa)
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Update an existing reserved static IP address configuration or metadata.

# Update



## OpenAPI

````yaml patch /reserved_addrs/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /reserved_addrs/{id}:
    patch:
      tags:
        - ReservedAddrs
      summary: Update
      description: |
        Update the attributes of a reserved address.
      operationId: ReservedAddrsUpdate
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ReservedAddrUpdate'
      responses:
        '200':
          description: |
            Update the attributes of a reserved address.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReservedAddr'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    ReservedAddrUpdate:
      type: object
      properties:
        id:
          description: n/a
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
    ReservedAddr:
      type: object
      properties:
        id:
          description: |
            unique reserved address resource identifier
          type: string
        uri:
          description: |
            URI of the reserved address API resource
          type: string
        created_at:
          description: |
            timestamp when the reserved address was created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
        addr:
          description: >
            hostname:port of the reserved address that was assigned at creation
            time
          type: string
        region:
          description: >
            reserve the address in this geographic ngrok datacenter. Optional,
            default is us. (au, eu, ap, us, jp, in, sa)
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Update an existing reserved static IP address configuration or metadata.

# Update



## OpenAPI

````yaml patch /reserved_addrs/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /reserved_addrs/{id}:
    patch:
      tags:
        - ReservedAddrs
      summary: Update
      description: |
        Update the attributes of a reserved address.
      operationId: ReservedAddrsUpdate
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ReservedAddrUpdate'
      responses:
        '200':
          description: |
            Update the attributes of a reserved address.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReservedAddr'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    ReservedAddrUpdate:
      type: object
      properties:
        id:
          description: n/a
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
    ReservedAddr:
      type: object
      properties:
        id:
          description: |
            unique reserved address resource identifier
          type: string
        uri:
          description: |
            URI of the reserved address API resource
          type: string
        created_at:
          description: |
            timestamp when the reserved address was created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
        addr:
          description: >
            hostname:port of the reserved address that was assigned at creation
            time
          type: string
        region:
          description: >
            reserve the address in this geographic ngrok datacenter. Optional,
            default is us. (au, eu, ap, us, jp, in, sa)
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Update an existing reserved static IP address configuration or metadata.

# Update



## OpenAPI

````yaml patch /reserved_addrs/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /reserved_addrs/{id}:
    patch:
      tags:
        - ReservedAddrs
      summary: Update
      description: |
        Update the attributes of a reserved address.
      operationId: ReservedAddrsUpdate
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ReservedAddrUpdate'
      responses:
        '200':
          description: |
            Update the attributes of a reserved address.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReservedAddr'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    ReservedAddrUpdate:
      type: object
      properties:
        id:
          description: n/a
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
    ReservedAddr:
      type: object
      properties:
        id:
          description: |
            unique reserved address resource identifier
          type: string
        uri:
          description: |
            URI of the reserved address API resource
          type: string
        created_at:
          description: |
            timestamp when the reserved address was created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
        addr:
          description: >
            hostname:port of the reserved address that was assigned at creation
            time
          type: string
        region:
          description: >
            reserve the address in this geographic ngrok datacenter. Optional,
            default is us. (au, eu, ap, us, jp, in, sa)
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Update an existing reserved static IP address configuration or metadata.

# Update



## OpenAPI

````yaml patch /reserved_addrs/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /reserved_addrs/{id}:
    patch:
      tags:
        - ReservedAddrs
      summary: Update
      description: |
        Update the attributes of a reserved address.
      operationId: ReservedAddrsUpdate
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ReservedAddrUpdate'
      responses:
        '200':
          description: |
            Update the attributes of a reserved address.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReservedAddr'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    ReservedAddrUpdate:
      type: object
      properties:
        id:
          description: n/a
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
    ReservedAddr:
      type: object
      properties:
        id:
          description: |
            unique reserved address resource identifier
          type: string
        uri:
          description: |
            URI of the reserved address API resource
          type: string
        created_at:
          description: |
            timestamp when the reserved address was created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of what this reserved address will be
            used for
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this reserved
            address. Optional, max 4096 bytes.
          type: string
        addr:
          description: >
            hostname:port of the reserved address that was assigned at creation
            time
          type: string
        region:
          description: >
            reserve the address in this geographic ngrok datacenter. Optional,
            default is us. (au, eu, ap, us, jp, in, sa)
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Delete the TLS certificate associated with a specific reserved domain.

# DeleteCertificate



## OpenAPI

````yaml delete /reserved_domains/{id}/certificate
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /reserved_domains/{id}/certificate:
    delete:
      tags:
        - ReservedDomains
      summary: DeleteCertificate
      description: |
        Detach the certificate attached to a reserved domain.
      operationId: ReservedDomainsDeleteCertificate
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            a resource identifier
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: |
            Detach the certificate attached to a reserved domain.
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Remove the certificate management policy from a specific reserved domain.

# DeleteCertificateManagementPolicy



## OpenAPI

````yaml delete /reserved_domains/{id}/certificate_management_policy
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /reserved_domains/{id}/certificate_management_policy:
    delete:
      tags:
        - ReservedDomains
      summary: DeleteCertificateManagementPolicy
      description: |
        Detach the certificate management policy attached to a reserved domain.
      operationId: ReservedDomainsDeleteCertificateManagementPolicy
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            a resource identifier
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: >
            Detach the certificate management policy attached to a reserved
            domain.
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Remove the certificate management policy from a specific reserved domain.

# DeleteCertificateManagementPolicy



## OpenAPI

````yaml delete /reserved_domains/{id}/certificate_management_policy
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /reserved_domains/{id}/certificate_management_policy:
    delete:
      tags:
        - ReservedDomains
      summary: DeleteCertificateManagementPolicy
      description: |
        Detach the certificate management policy attached to a reserved domain.
      operationId: ReservedDomainsDeleteCertificateManagementPolicy
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            a resource identifier
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: >
            Detach the certificate management policy attached to a reserved
            domain.
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Remove the certificate management policy from a specific reserved domain.

# DeleteCertificateManagementPolicy



## OpenAPI

````yaml delete /reserved_domains/{id}/certificate_management_policy
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /reserved_domains/{id}/certificate_management_policy:
    delete:
      tags:
        - ReservedDomains
      summary: DeleteCertificateManagementPolicy
      description: |
        Detach the certificate management policy attached to a reserved domain.
      operationId: ReservedDomainsDeleteCertificateManagementPolicy
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            a resource identifier
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: >
            Detach the certificate management policy attached to a reserved
            domain.
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Upload a new TLS certificate for use with your ngrok edges and reserved domains.

# Create



## OpenAPI

````yaml post /tls_certificates
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /tls_certificates:
    post:
      tags:
        - TLSCertificates
      summary: Create
      description: |
        Upload a new TLS certificate
      operationId: TlsCertificatesCreate
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TLSCertificateCreate'
      responses:
        '201':
          description: |
            Upload a new TLS certificate
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TLSCertificate'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    TLSCertificateCreate:
      type: object
      required:
        - certificate_pem
        - private_key_pem
      properties:
        description:
          description: >
            human-readable description of this TLS certificate. optional, max
            255 bytes.
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this TLS
            certificate. optional, max 4096 bytes.
          type: string
        certificate_pem:
          description: >
            chain of PEM-encoded certificates, leaf first. See [Certificate
            Bundles](https://ngrok.com/docs/cloud-edge/endpoints#certificate-chains).
          type: string
        private_key_pem:
          description: >
            private key for the TLS certificate, PEM-encoded. See [Private
            Keys](https://ngrok.com/docs/cloud-edge/endpoints#private-keys).
          type: string
    TLSCertificate:
      type: object
      properties:
        id:
          description: |
            unique identifier for this TLS certificate
          type: string
        uri:
          description: |
            URI of the TLS certificate API resource
          type: string
        created_at:
          description: |
            timestamp when the TLS certificate was created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of this TLS certificate. optional, max
            255 bytes.
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this TLS
            certificate. optional, max 4096 bytes.
          type: string
        certificate_pem:
          description: >
            chain of PEM-encoded certificates, leaf first. See [Certificate
            Bundles](https://ngrok.com/docs/cloud-edge/endpoints#certificate-chains).
          type: string
        subject_common_name:
          description: |
            subject common name from the leaf of this TLS certificate
          type: string
        subject_alternative_names:
          $ref: '#/components/schemas/TLSCertificateSANs'
          description: >
            subject alternative names (SANs) from the leaf of this TLS
            certificate
        issued_at:
          description: >
            timestamp (in RFC 3339 format) when this TLS certificate was issued
            automatically, or null if this certificate was user-uploaded
          type: string
        not_before:
          description: |
            timestamp when this TLS certificate becomes valid, RFC 3339 format
          type: string
        not_after:
          description: |
            timestamp when this TLS certificate becomes invalid, RFC 3339 format
          type: string
        key_usages:
          description: >
            set of actions the private key of this TLS certificate can be used
            for
          type: array
          items:
            type: string
        extended_key_usages:
          description: >
            extended set of actions the private key of this TLS certificate can
            be used for
          type: array
          items:
            type: string
        private_key_type:
          description: >
            type of the private key of this TLS certificate. One of rsa, ecdsa,
            or ed25519.
          type: string
        issuer_common_name:
          description: |
            issuer common name from the leaf of this TLS certificate
          type: string
        serial_number:
          description: |
            serial number of the leaf of this TLS certificate
          type: string
        subject_organization:
          description: |
            subject organization from the leaf of this TLS certificate
          type: string
        subject_organizational_unit:
          description: |
            subject organizational unit from the leaf of this TLS certificate
          type: string
        subject_locality:
          description: |
            subject locality from the leaf of this TLS certificate
          type: string
        subject_province:
          description: |
            subject province from the leaf of this TLS certificate
          type: string
        subject_country:
          description: |
            subject country from the leaf of this TLS certificate
          type: string
    TLSCertificateSANs:
      type: object
      properties:
        dns_names:
          description: >
            set of additional domains (including wildcards) this TLS certificate
            is valid for
          type: array
          items:
            type: string
        ips:
          description: |
            set of IP addresses this TLS certificate is also valid for
          type: array
          items:
            type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Retrieve details about a specific TLS certificate including its domains and expiration date.

# Get



## OpenAPI

````yaml get /tls_certificates/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /tls_certificates/{id}:
    get:
      tags:
        - TLSCertificates
      summary: Get
      description: |
        Get detailed information about a TLS certificate
      operationId: TlsCertificatesGet
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            a resource identifier
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: |
            Get detailed information about a TLS certificate
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TLSCertificate'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    TLSCertificate:
      type: object
      properties:
        id:
          description: |
            unique identifier for this TLS certificate
          type: string
        uri:
          description: |
            URI of the TLS certificate API resource
          type: string
        created_at:
          description: |
            timestamp when the TLS certificate was created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of this TLS certificate. optional, max
            255 bytes.
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this TLS
            certificate. optional, max 4096 bytes.
          type: string
        certificate_pem:
          description: >
            chain of PEM-encoded certificates, leaf first. See [Certificate
            Bundles](https://ngrok.com/docs/cloud-edge/endpoints#certificate-chains).
          type: string
        subject_common_name:
          description: |
            subject common name from the leaf of this TLS certificate
          type: string
        subject_alternative_names:
          $ref: '#/components/schemas/TLSCertificateSANs'
          description: >
            subject alternative names (SANs) from the leaf of this TLS
            certificate
        issued_at:
          description: >
            timestamp (in RFC 3339 format) when this TLS certificate was issued
            automatically, or null if this certificate was user-uploaded
          type: string
        not_before:
          description: |
            timestamp when this TLS certificate becomes valid, RFC 3339 format
          type: string
        not_after:
          description: |
            timestamp when this TLS certificate becomes invalid, RFC 3339 format
          type: string
        key_usages:
          description: >
            set of actions the private key of this TLS certificate can be used
            for
          type: array
          items:
            type: string
        extended_key_usages:
          description: >
            extended set of actions the private key of this TLS certificate can
            be used for
          type: array
          items:
            type: string
        private_key_type:
          description: >
            type of the private key of this TLS certificate. One of rsa, ecdsa,
            or ed25519.
          type: string
        issuer_common_name:
          description: |
            issuer common name from the leaf of this TLS certificate
          type: string
        serial_number:
          description: |
            serial number of the leaf of this TLS certificate
          type: string
        subject_organization:
          description: |
            subject organization from the leaf of this TLS certificate
          type: string
        subject_organizational_unit:
          description: |
            subject organizational unit from the leaf of this TLS certificate
          type: string
        subject_locality:
          description: |
            subject locality from the leaf of this TLS certificate
          type: string
        subject_province:
          description: |
            subject province from the leaf of this TLS certificate
          type: string
        subject_country:
          description: |
            subject country from the leaf of this TLS certificate
          type: string
    TLSCertificateSANs:
      type: object
      properties:
        dns_names:
          description: >
            set of additional domains (including wildcards) this TLS certificate
            is valid for
          type: array
          items:
            type: string
        ips:
          description: |
            set of IP addresses this TLS certificate is also valid for
          type: array
          items:
            type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Retrieve details about a specific TLS certificate including its domains and expiration date.

# Get



## OpenAPI

````yaml get /tls_certificates/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /tls_certificates/{id}:
    get:
      tags:
        - TLSCertificates
      summary: Get
      description: |
        Get detailed information about a TLS certificate
      operationId: TlsCertificatesGet
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            a resource identifier
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: |
            Get detailed information about a TLS certificate
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TLSCertificate'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    TLSCertificate:
      type: object
      properties:
        id:
          description: |
            unique identifier for this TLS certificate
          type: string
        uri:
          description: |
            URI of the TLS certificate API resource
          type: string
        created_at:
          description: |
            timestamp when the TLS certificate was created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of this TLS certificate. optional, max
            255 bytes.
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this TLS
            certificate. optional, max 4096 bytes.
          type: string
        certificate_pem:
          description: >
            chain of PEM-encoded certificates, leaf first. See [Certificate
            Bundles](https://ngrok.com/docs/cloud-edge/endpoints#certificate-chains).
          type: string
        subject_common_name:
          description: |
            subject common name from the leaf of this TLS certificate
          type: string
        subject_alternative_names:
          $ref: '#/components/schemas/TLSCertificateSANs'
          description: >
            subject alternative names (SANs) from the leaf of this TLS
            certificate
        issued_at:
          description: >
            timestamp (in RFC 3339 format) when this TLS certificate was issued
            automatically, or null if this certificate was user-uploaded
          type: string
        not_before:
          description: |
            timestamp when this TLS certificate becomes valid, RFC 3339 format
          type: string
        not_after:
          description: |
            timestamp when this TLS certificate becomes invalid, RFC 3339 format
          type: string
        key_usages:
          description: >
            set of actions the private key of this TLS certificate can be used
            for
          type: array
          items:
            type: string
        extended_key_usages:
          description: >
            extended set of actions the private key of this TLS certificate can
            be used for
          type: array
          items:
            type: string
        private_key_type:
          description: >
            type of the private key of this TLS certificate. One of rsa, ecdsa,
            or ed25519.
          type: string
        issuer_common_name:
          description: |
            issuer common name from the leaf of this TLS certificate
          type: string
        serial_number:
          description: |
            serial number of the leaf of this TLS certificate
          type: string
        subject_organization:
          description: |
            subject organization from the leaf of this TLS certificate
          type: string
        subject_organizational_unit:
          description: |
            subject organizational unit from the leaf of this TLS certificate
          type: string
        subject_locality:
          description: |
            subject locality from the leaf of this TLS certificate
          type: string
        subject_province:
          description: |
            subject province from the leaf of this TLS certificate
          type: string
        subject_country:
          description: |
            subject country from the leaf of this TLS certificate
          type: string
    TLSCertificateSANs:
      type: object
      properties:
        dns_names:
          description: >
            set of additional domains (including wildcards) this TLS certificate
            is valid for
          type: array
          items:
            type: string
        ips:
          description: |
            set of IP addresses this TLS certificate is also valid for
          type: array
          items:
            type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Update an existing TLS certificate with new certificate data or private key.

# Update



## OpenAPI

````yaml patch /tls_certificates/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /tls_certificates/{id}:
    patch:
      tags:
        - TLSCertificates
      summary: Update
      description: |
        Update attributes of a TLS Certificate by ID
      operationId: TlsCertificatesUpdate
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TLSCertificateUpdate'
      responses:
        '200':
          description: |
            Update attributes of a TLS Certificate by ID
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TLSCertificate'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    TLSCertificateUpdate:
      type: object
      properties:
        id:
          description: n/a
          type: string
        description:
          description: >
            human-readable description of this TLS certificate. optional, max
            255 bytes.
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this TLS
            certificate. optional, max 4096 bytes.
          type: string
    TLSCertificate:
      type: object
      properties:
        id:
          description: |
            unique identifier for this TLS certificate
          type: string
        uri:
          description: |
            URI of the TLS certificate API resource
          type: string
        created_at:
          description: |
            timestamp when the TLS certificate was created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of this TLS certificate. optional, max
            255 bytes.
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this TLS
            certificate. optional, max 4096 bytes.
          type: string
        certificate_pem:
          description: >
            chain of PEM-encoded certificates, leaf first. See [Certificate
            Bundles](https://ngrok.com/docs/cloud-edge/endpoints#certificate-chains).
          type: string
        subject_common_name:
          description: |
            subject common name from the leaf of this TLS certificate
          type: string
        subject_alternative_names:
          $ref: '#/components/schemas/TLSCertificateSANs'
          description: >
            subject alternative names (SANs) from the leaf of this TLS
            certificate
        issued_at:
          description: >
            timestamp (in RFC 3339 format) when this TLS certificate was issued
            automatically, or null if this certificate was user-uploaded
          type: string
        not_before:
          description: |
            timestamp when this TLS certificate becomes valid, RFC 3339 format
          type: string
        not_after:
          description: |
            timestamp when this TLS certificate becomes invalid, RFC 3339 format
          type: string
        key_usages:
          description: >
            set of actions the private key of this TLS certificate can be used
            for
          type: array
          items:
            type: string
        extended_key_usages:
          description: >
            extended set of actions the private key of this TLS certificate can
            be used for
          type: array
          items:
            type: string
        private_key_type:
          description: >
            type of the private key of this TLS certificate. One of rsa, ecdsa,
            or ed25519.
          type: string
        issuer_common_name:
          description: |
            issuer common name from the leaf of this TLS certificate
          type: string
        serial_number:
          description: |
            serial number of the leaf of this TLS certificate
          type: string
        subject_organization:
          description: |
            subject organization from the leaf of this TLS certificate
          type: string
        subject_organizational_unit:
          description: |
            subject organizational unit from the leaf of this TLS certificate
          type: string
        subject_locality:
          description: |
            subject locality from the leaf of this TLS certificate
          type: string
        subject_province:
          description: |
            subject province from the leaf of this TLS certificate
          type: string
        subject_country:
          description: |
            subject country from the leaf of this TLS certificate
          type: string
    TLSCertificateSANs:
      type: object
      properties:
        dns_names:
          description: >
            set of additional domains (including wildcards) this TLS certificate
            is valid for
          type: array
          items:
            type: string
        ips:
          description: |
            set of IP addresses this TLS certificate is also valid for
          type: array
          items:
            type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> List all event destination configurations in your ngrok account with optional filtering.

# List



## OpenAPI

````yaml get /event_destinations
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /event_destinations:
    get:
      tags:
        - EventDestinations
      summary: List
      description: |
        List all Event Destinations on this account.
      operationId: EventDestinationsList
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: before_id
          description: >
            Expects a resource ID as its input. Returns earlier entries in the
            result set, sorted by ID.
          in: query
          required: false
          schema:
            type: string
        - name: limit
          description: >
            Constrains the number of results in the dataset. See the [API
            Overview](https://ngrok.com/docs/api/index#pagination) for details.
          in: query
          required: false
          schema:
            type: string
        - name: filter
          description: >
            A CEL expression to filter the list results. Supports logical and
            comparison operators to match on fields such as `id`, `metadata`,
            `created_at`, and more. See ngrok API Filtering for syntax and field
            details: https://ngrok.com/docs/api/api-filtering.
          in: query
          required: false
          schema:
            type: string
      responses:
        '200':
          description: |
            List all Event Destinations on this account.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EventDestinationList'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    EventDestinationList:
      type: object
      properties:
        event_destinations:
          description: |
            The list of all Event Destinations on this account.
          type: array
          items:
            $ref: '#/components/schemas/EventDestination'
        uri:
          description: |
            URI of the Event Destinations list API resource.
          type: string
        next_page_uri:
          description: |
            URI of the next page, or null if there is no next page.
          type: string
    EventDestination:
      type: object
      properties:
        id:
          description: |
            Unique identifier for this Event Destination.
          type: string
        metadata:
          description: >
            Arbitrary user-defined machine-readable data of this Event
            Destination. Optional, max 4096 bytes.
          type: string
        created_at:
          description: |
            Timestamp when the Event Destination was created, RFC 3339 format.
          type: string
        description:
          description: >
            Human-readable description of the Event Destination. Optional, max
            255 bytes.
          type: string
        format:
          description: >
            The output format you would like to serialize events into when
            sending to their target. Currently the only accepted value is
            `JSON`.
          type: string
        target:
          $ref: '#/components/schemas/EventTarget'
          description: >
            An object that encapsulates where and how to send your events. An
            event destination must contain exactly one of the following objects,
            leaving the rest null: `kinesis`, `firehose`, `cloudwatch_logs`, or
            `s3`.
        uri:
          description: |
            URI of the Event Destination API resource.
          type: string
    EventTarget:
      type: object
      properties:
        firehose:
          $ref: '#/components/schemas/EventTargetFirehose'
          description: |
            Configuration used to send events to Amazon Kinesis Data Firehose.
        kinesis:
          $ref: '#/components/schemas/EventTargetKinesis'
          description: |
            Configuration used to send events to Amazon Kinesis.
        cloudwatch_logs:
          $ref: '#/components/schemas/EventTargetCloudwatchLogs'
          description: |
            Configuration used to send events to Amazon CloudWatch Logs.
        datadog:
          $ref: '#/components/schemas/EventTargetDatadog'
          description: |
            Configuration used to send events to Datadog.
        azure_logs_ingestion:
          $ref: '#/components/schemas/EventTargetAzureLogsIngestion'
          description: n/a
    EventTargetFirehose:
      type: object
      properties:
        auth:
          $ref: '#/components/schemas/AWSAuth'
          description: >
            Configuration for how to authenticate into your AWS account. Exactly
            one of `role` or `creds` should be configured.
        delivery_stream_arn:
          description: >
            An Amazon Resource Name specifying the Firehose delivery stream to
            deposit events into.
          type: string
    EventTargetKinesis:
      type: object
      properties:
        auth:
          $ref: '#/components/schemas/AWSAuth'
          description: >
            Configuration for how to authenticate into your AWS account. Exactly
            one of `role` or `creds` should be configured.
        stream_arn:
          description: >
            An Amazon Resource Name specifying the Kinesis stream to deposit
            events into.
          type: string
    EventTargetCloudwatchLogs:
      type: object
      properties:
        auth:
          $ref: '#/components/schemas/AWSAuth'
          description: >
            Configuration for how to authenticate into your AWS account. Exactly
            one of `role` or `creds` should be configured.
        log_group_arn:
          description: >
            An Amazon Resource Name specifying the CloudWatch Logs group to
            deposit events into.
          type: string
    EventTargetDatadog:
      type: object
      properties:
        api_key:
          description: |
            Datadog API key to use.
          type: string
        ddtags:
          description: |
            Tags to send with the event.
          type: string
        service:
          description: |
            Service name to send with the event.
          type: string
        ddsite:
          description: |
            Datadog site to send event to.
          type: string
    EventTargetAzureLogsIngestion:
      type: object
      required:
        - tenant_id
        - client_id
        - client_secret
        - logs_ingestion_uri
        - data_collection_rule_id
        - data_collection_stream_name
      properties:
        tenant_id:
          description: |
            Tenant ID for the Azure account
          type: string
        client_id:
          description: |
            Client ID for the application client
          type: string
        client_secret:
          description: |
            Client Secret for the application client
          type: string
        logs_ingestion_uri:
          description: |
            Data collection endpoint logs ingestion URI
          type: string
        data_collection_rule_id:
          description: |
            Data collection rule immutable ID
          type: string
        data_collection_stream_name:
          description: >
            Data collection stream name to use as destination, located inside
            the DCR
          type: string
    AWSAuth:
      type: object
      properties:
        role:
          $ref: '#/components/schemas/AWSRole'
          description: >
            A role for ngrok to assume on your behalf to deposit events into
            your AWS account.
        creds:
          $ref: '#/components/schemas/AWSCredentials'
          description: >
            Credentials to your AWS account if you prefer ngrok to sign in with
            long-term access keys.
    AWSRole:
      type: object
      required:
        - role_arn
      properties:
        role_arn:
          description: >
            An ARN that specifies the role that ngrok should use to deliver to
            the configured target.
          type: string
    AWSCredentials:
      type: object
      required:
        - aws_access_key_id
        - aws_secret_access_key
      properties:
        aws_access_key_id:
          description: |
            The ID portion of an AWS access key.
          type: string
        aws_secret_access_key:
          description: |
            The secret portion of an AWS access key.
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Service Users (Bot Users)

> Service Users API reference.

<Note>
  Service Users were previously called Bot Users.

  The Bot User API endpoint is still available but will be deprecated in the future.
  If you need the Bot Users API reference, you can find it [here](/api-reference/botusers/get).
</Note>

## Create Service User

Create a new Service User.

### Request

`POST /service_users`

#### Example request

```bash  theme={null}
curl \
-X POST \
-H "Authorization: Bearer {API_KEY}" \
-H "Content-Type: application/json" \
-H "Ngrok-Version: 2" \
-d '{"name":"new service user from API"}' \
https://api.ngrok.com/service_users
```

#### Parameters

| Name     | Type    | Description                                            |
| -------- | ------- | ------------------------------------------------------ |
| `name`   | string  | Human-readable name used to identify the Service User. |
| `active` | boolean | Whether or not the Service User is active.             |

### Response

Returns a 201 response on success.

#### Example response

```json  theme={null}
{
  "active": true,
  "created_at": "2025-09-04T10:11:43Z",
  "id": "service_32ELIFubEAAGUeRtreNW6kr94Od",
  "name": "new service user from API",
  "uri": "https://api.ngrok.com/service_users/service_32ELIFubEAAGUeRtreNW6kr94Od"
}
```

#### Fields

| Name         | Type    | Description                                                 |
| ------------ | ------- | ----------------------------------------------------------- |
| `id`         | string  | Unique API key resource identifier.                         |
| `uri`        | string  | URI to the API resource of this Service User                |
| `name`       | string  | Human-readable name used to identify the Service User.      |
| `active`     | boolean | Whether or not the Service User is active.                  |
| `created_at` | string  | Timestamp when the API key was created, in RFC 3339 format. |

## Delete Service User

Delete a Service User by ID.

### Request

`DELETE /service_users/\{id\}`

#### Example request

```bash  theme={null}
curl \
-X DELETE \
-H "Authorization: Bearer {API_KEY}" \
-H "Ngrok-Version: 2" \
https://api.ngrok.com/service_users/service_32ELIFubEAAGUeRtreNW6kr94Od
```

### Response

Returns a 204 response with no body on success.

## Get Service User

Get the details of a Service User by ID.

### Request

`GET /service_users/\{id\}`

#### Example request

```bash  theme={null}
curl \
-X GET \
-H "Authorization: Bearer {API_KEY}" \
-H "Ngrok-Version: 2" \
https://api.ngrok.com/service_users/service_32ELIFubEAAGUeRtreNW6kr94Od
```

### Response

Returns a 200 response on success.

#### Example response

```json  theme={null}
{
  "active": true,
  "created_at": "2025-09-04T10:11:43Z",
  "id": "service_32ELIFubEAAGUeRtreNW6kr94Od",
  "name": "new service user from API",
  "uri": "https://api.ngrok.com/service_users/service_32ELIFubEAAGUeRtreNW6kr94Od"
}
```

#### Fields

| Name         | Type    | Description                                                 |
| ------------ | ------- | ----------------------------------------------------------- |
| `id`         | string  | Unique API key resource identifier.                         |
| `uri`        | string  | URI to the API resource of this Service User.               |
| `name`       | string  | Human-readable name used to identify the Service User.      |
| `active`     | boolean | Whether or not the Service User is active.                  |
| `created_at` | string  | Timestamp when the API key was created, in RFC 3339 format. |

## List Service Users

List all Service Users in this account.

### Request

`GET /service_users`

#### Example request

```bash  theme={null}
curl \
-X GET \
-H "Authorization: Bearer {API_KEY}" \
-H "Ngrok-Version: 2" \
https://api.ngrok.com/service_users?limit=1
```

### Response

Returns a 200 response on success.

#### Example response

```json  theme={null}
{
  "service_users": [
    {
      "active": true,
      "created_at": "2025-09-04T10:11:43Z",
      "id": "service_32ELIKFMeMYDQm0tERqc5MmICl4",
      "name": "API example service user",
      "uri": "https://api.ngrok.com/service_users/service_32ELIKFMeMYDQm0tERqc5MmICl4"
    }
  ],
  "next_page_uri": "https://api.ngrok.com/service_users?before_id=service_32ELIKFMeMYDQm0tERqc5MmICl4&limit=1",
  "uri": "https://api.ngrok.com/service_users"
}
```

#### Fields

| Name            | Type                               | Description                                             |
| --------------- | ---------------------------------- | ------------------------------------------------------- |
| `service_users` | [ServiceUser](#serviceuser-fields) | List of all Service Users on this account.              |
| `uri`           | string                             | URI of the Service Users list API resource.             |
| `next_page_uri` | string                             | URI of the next page, or null if there is no next page. |

#### ServiceUser fields

| Name         | Type    | Description                                                 |
| ------------ | ------- | ----------------------------------------------------------- |
| `id`         | string  | Unique API key resource identifier.                         |
| `uri`        | string  | URI to the API resource of this Service User.               |
| `name`       | string  | Human-readable name used to identify the Service User.      |
| `active`     | boolean | Whether or not the Service User is active.                  |
| `created_at` | string  | Timestamp when the API key was created, in RFC 3339 format. |

## Update Service User

Update attributes of a Service User by ID.

### Request

`PATCH /service_users/\{id\}`

#### Example request

```bash  theme={null}
curl \
-X PATCH \
-H "Authorization: Bearer {API_KEY}" \
-H "Content-Type: application/json" \
-H "Ngrok-Version: 2" \
-d '{"active":false,"name":"inactive service user from API"}' \
https://api.ngrok.com/service_users/service_32ELIFubEAAGUeRtreNW6kr94Od
```

#### Parameters

| Name     | Type    | Description                                            |
| -------- | ------- | ------------------------------------------------------ |
| `id`     | string  |                                                        |
| `name`   | string  | Human-readable name used to identify the Service User. |
| `active` | boolean | Whether or not the Service User is active.             |

### Response

Returns a 200 response and a copy of the updated entity on success.

#### Example response

```json  theme={null}
{
  "active": false,
  "created_at": "2025-09-04T10:11:43Z",
  "id": "service_32ELIFubEAAGUeRtreNW6kr94Od",
  "name": "inactive service user from API",
  "uri": "https://api.ngrok.com/service_users/service_32ELIFubEAAGUeRtreNW6kr94Od"
}
```

#### Fields

| Name         | Type    | Description                                                 |
| ------------ | ------- | ----------------------------------------------------------- |
| `id`         | string  | Unique API key resource identifier.                         |
| `uri`        | string  | URI to the API resource of this Service User.               |
| `name`       | string  | Human-readable name used to identify the Service User.      |
| `active`     | boolean | Whether or not the Service User is active.                  |
| `created_at` | string  | Timestamp when the API key was created, in RFC 3339 format. |


Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> List all SSH certificate authorities in your ngrok account with optional filtering.

# List



## OpenAPI

````yaml get /ssh_certificate_authorities
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /ssh_certificate_authorities:
    get:
      tags:
        - SSHCertificateAuthorities
      summary: List
      description: |
        List all SSH Certificate Authorities on this account
      operationId: SshCertificateAuthoritiesList
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: before_id
          description: >
            Expects a resource ID as its input. Returns earlier entries in the
            result set, sorted by ID.
          in: query
          required: false
          schema:
            type: string
        - name: limit
          description: >
            Constrains the number of results in the dataset. See the [API
            Overview](https://ngrok.com/docs/api/index#pagination) for details.
          in: query
          required: false
          schema:
            type: string
        - name: filter
          description: >
            A CEL expression to filter the list results. Supports logical and
            comparison operators to match on fields such as `id`, `metadata`,
            `created_at`, and more. See ngrok API Filtering for syntax and field
            details: https://ngrok.com/docs/api/api-filtering.
          in: query
          required: false
          schema:
            type: string
      responses:
        '200':
          description: |
            List all SSH Certificate Authorities on this account
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SSHCertificateAuthorityList'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    SSHCertificateAuthorityList:
      type: object
      properties:
        ssh_certificate_authorities:
          description: |
            the list of all certificate authorities on this account
          type: array
          items:
            $ref: '#/components/schemas/SSHCertificateAuthority'
        uri:
          description: |
            URI of the certificates authorities list API resource
          type: string
        next_page_uri:
          description: |
            URI of the next page, or null if there is no next page
          type: string
    SSHCertificateAuthority:
      type: object
      properties:
        id:
          description: |
            unique identifier for this SSH Certificate Authority
          type: string
        uri:
          description: |
            URI of the SSH Certificate Authority API resource
          type: string
        created_at:
          description: >
            timestamp when the SSH Certificate Authority API resource was
            created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of this SSH Certificate Authority.
            optional, max 255 bytes.
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this SSH Certificate
            Authority. optional, max 4096 bytes.
          type: string
        public_key:
          description: |
            raw public key for this SSH Certificate Authority
          type: string
        key_type:
          description: |
            the type of private key for this SSH Certificate Authority
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Create a new SSH certificate authority for signing SSH host and user certificates.

# Create



## OpenAPI

````yaml post /ssh_certificate_authorities
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /ssh_certificate_authorities:
    post:
      tags:
        - SSHCertificateAuthorities
      summary: Create
      description: |
        Create a new SSH Certificate Authority
      operationId: SshCertificateAuthoritiesCreate
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SSHCertificateAuthorityCreate'
      responses:
        '201':
          description: |
            Create a new SSH Certificate Authority
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SSHCertificateAuthority'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    SSHCertificateAuthorityCreate:
      type: object
      properties:
        description:
          description: >
            human-readable description of this SSH Certificate Authority.
            optional, max 255 bytes.
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this SSH Certificate
            Authority. optional, max 4096 bytes.
          type: string
        private_key_type:
          description: >
            the type of private key to generate. one of `rsa`, `ecdsa`,
            `ed25519`
          type: string
        elliptic_curve:
          description: |
            the type of elliptic curve to use when creating an ECDSA key
          type: string
        key_size:
          description: >
            the key size to use when creating an RSA key. one of `2048` or
            `4096`
          type: integer
    SSHCertificateAuthority:
      type: object
      properties:
        id:
          description: |
            unique identifier for this SSH Certificate Authority
          type: string
        uri:
          description: |
            URI of the SSH Certificate Authority API resource
          type: string
        created_at:
          description: >
            timestamp when the SSH Certificate Authority API resource was
            created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of this SSH Certificate Authority.
            optional, max 255 bytes.
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this SSH Certificate
            Authority. optional, max 4096 bytes.
          type: string
        public_key:
          description: |
            raw public key for this SSH Certificate Authority
          type: string
        key_type:
          description: |
            the type of private key for this SSH Certificate Authority
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Retrieve details about a specific SSH certificate authority including its public key.

# Get



## OpenAPI

````yaml get /ssh_certificate_authorities/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /ssh_certificate_authorities/{id}:
    get:
      tags:
        - SSHCertificateAuthorities
      summary: Get
      description: |
        Get detailed information about an SSH Certificate Authority
      operationId: SshCertificateAuthoritiesGet
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            a resource identifier
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: |
            Get detailed information about an SSH Certificate Authority
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SSHCertificateAuthority'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    SSHCertificateAuthority:
      type: object
      properties:
        id:
          description: |
            unique identifier for this SSH Certificate Authority
          type: string
        uri:
          description: |
            URI of the SSH Certificate Authority API resource
          type: string
        created_at:
          description: >
            timestamp when the SSH Certificate Authority API resource was
            created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of this SSH Certificate Authority.
            optional, max 255 bytes.
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this SSH Certificate
            Authority. optional, max 4096 bytes.
          type: string
        public_key:
          description: |
            raw public key for this SSH Certificate Authority
          type: string
        key_type:
          description: |
            the type of private key for this SSH Certificate Authority
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Delete a specific SSH certificate authority by its unique identifier.

# Delete



## OpenAPI

````yaml delete /ssh_certificate_authorities/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /ssh_certificate_authorities/{id}:
    delete:
      tags:
        - SSHCertificateAuthorities
      summary: Delete
      description: |
        Delete an SSH Certificate Authority
      operationId: SshCertificateAuthoritiesDelete
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            a resource identifier
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: |
            Delete an SSH Certificate Authority
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Update an existing SSH certificate authority with new metadata or description.

# Update



## OpenAPI

````yaml patch /ssh_certificate_authorities/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /ssh_certificate_authorities/{id}:
    patch:
      tags:
        - SSHCertificateAuthorities
      summary: Update
      description: |
        Update an SSH Certificate Authority
      operationId: SshCertificateAuthoritiesUpdate
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SSHCertificateAuthorityUpdate'
      responses:
        '200':
          description: |
            Update an SSH Certificate Authority
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SSHCertificateAuthority'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    SSHCertificateAuthorityUpdate:
      type: object
      properties:
        id:
          description: n/a
          type: string
        description:
          description: >
            human-readable description of this SSH Certificate Authority.
            optional, max 255 bytes.
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this SSH Certificate
            Authority. optional, max 4096 bytes.
          type: string
    SSHCertificateAuthority:
      type: object
      properties:
        id:
          description: |
            unique identifier for this SSH Certificate Authority
          type: string
        uri:
          description: |
            URI of the SSH Certificate Authority API resource
          type: string
        created_at:
          description: >
            timestamp when the SSH Certificate Authority API resource was
            created, RFC 3339 format
          type: string
        description:
          description: >
            human-readable description of this SSH Certificate Authority.
            optional, max 255 bytes.
          type: string
        metadata:
          description: >
            arbitrary user-defined machine-readable data of this SSH Certificate
            Authority. optional, max 4096 bytes.
          type: string
        public_key:
          description: |
            raw public key for this SSH Certificate Authority
          type: string
        key_type:
          description: |
            the type of private key for this SSH Certificate Authority
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> List all vault secrets in your ngrok account with optional filtering and pagination support.

# List



## OpenAPI

````yaml get /vault_secrets
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /vault_secrets:
    get:
      tags:
        - Secrets
      summary: List
      description: |
        List all Secrets owned by account
      operationId: SecretsList
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: before_id
          description: >
            Expects a resource ID as its input. Returns earlier entries in the
            result set, sorted by ID.
          in: query
          required: false
          schema:
            type: string
        - name: limit
          description: >
            Constrains the number of results in the dataset. See the [API
            Overview](https://ngrok.com/docs/api/index#pagination) for details.
          in: query
          required: false
          schema:
            type: string
        - name: filter
          description: >
            A CEL expression to filter the list results. Supports logical and
            comparison operators to match on fields such as `id`, `metadata`,
            `created_at`, and more. See ngrok API Filtering for syntax and field
            details: https://ngrok.com/docs/api/api-filtering.
          in: query
          required: false
          schema:
            type: string
      responses:
        '200':
          description: |
            List all Secrets owned by account
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SecretList'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    SecretList:
      type: object
      properties:
        secrets:
          description: |
            The list of Secrets for this account
          type: array
          items:
            $ref: '#/components/schemas/Secret'
        uri:
          description: n/a
          type: string
        next_page_uri:
          description: |
            URI of the next page of results, or null if there is no next page
          type: string
    Secret:
      type: object
      properties:
        id:
          description: |
            identifier for Secret
          type: string
        uri:
          description: |
            URI of this Secret API resource
          type: string
        created_at:
          description: |
            Timestamp when the Secret was created (RFC 3339 format)
          type: string
        updated_at:
          description: |
            Timestamp when the Secret was last updated (RFC 3339 format)
          type: string
        name:
          description: |
            Name of secret
          type: string
        description:
          description: |
            description of Secret
          type: string
        metadata:
          description: |
            Arbitrary user-defined metadata for this Secret
          type: string
        created_by:
          $ref: '#/components/schemas/Ref'
          description: |
            Reference to who created this Secret
        last_updated_by:
          $ref: '#/components/schemas/Ref'
          description: |
            Reference to who created this Secret
        vault:
          $ref: '#/components/schemas/Ref'
          description: |
            Reference to the vault the secret is stored in
        vault_name:
          description: |
            Name of the vault the secret is stored in
          type: string
    Ref:
      type: object
      properties:
        id:
          description: |
            a resource identifier
          type: string
        uri:
          description: |
            a uri for locating a resource
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Create a new vault secret for securely storing sensitive values used in ngrok configurations.

# Create



## OpenAPI

````yaml post /vault_secrets
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /vault_secrets:
    post:
      tags:
        - Secrets
      summary: Create
      description: |
        Create a new Secret
      operationId: SecretsCreate
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SecretCreate'
      responses:
        '201':
          description: |
            Create a new Secret
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Secret'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    SecretCreate:
      type: object
      properties:
        name:
          description: |
            Name of secret
          type: string
        value:
          description: |
            Value of secret
          type: string
        metadata:
          description: |
            Arbitrary user-defined metadata for this Secret
          type: string
        description:
          description: |
            description of Secret
          type: string
        vault_id:
          description: |
            unique identifier of the referenced vault
          type: string
        vault_name:
          description: |
            name of the referenced vault
          type: string
    Secret:
      type: object
      properties:
        id:
          description: |
            identifier for Secret
          type: string
        uri:
          description: |
            URI of this Secret API resource
          type: string
        created_at:
          description: |
            Timestamp when the Secret was created (RFC 3339 format)
          type: string
        updated_at:
          description: |
            Timestamp when the Secret was last updated (RFC 3339 format)
          type: string
        name:
          description: |
            Name of secret
          type: string
        description:
          description: |
            description of Secret
          type: string
        metadata:
          description: |
            Arbitrary user-defined metadata for this Secret
          type: string
        created_by:
          $ref: '#/components/schemas/Ref'
          description: |
            Reference to who created this Secret
        last_updated_by:
          $ref: '#/components/schemas/Ref'
          description: |
            Reference to who created this Secret
        vault:
          $ref: '#/components/schemas/Ref'
          description: |
            Reference to the vault the secret is stored in
        vault_name:
          description: |
            Name of the vault the secret is stored in
          type: string
    Ref:
      type: object
      properties:
        id:
          description: |
            a resource identifier
          type: string
        uri:
          description: |
            a uri for locating a resource
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Retrieve metadata about a specific vault secret. The secret value itself is never returned.

# Get



## OpenAPI

````yaml get /vault_secrets/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /vault_secrets/{id}:
    get:
      tags:
        - Secrets
      summary: Get
      description: |
        Get a Secret by ID
      operationId: SecretsGet
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            a resource identifier
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: |
            Get a Secret by ID
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Secret'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    Secret:
      type: object
      properties:
        id:
          description: |
            identifier for Secret
          type: string
        uri:
          description: |
            URI of this Secret API resource
          type: string
        created_at:
          description: |
            Timestamp when the Secret was created (RFC 3339 format)
          type: string
        updated_at:
          description: |
            Timestamp when the Secret was last updated (RFC 3339 format)
          type: string
        name:
          description: |
            Name of secret
          type: string
        description:
          description: |
            description of Secret
          type: string
        metadata:
          description: |
            Arbitrary user-defined metadata for this Secret
          type: string
        created_by:
          $ref: '#/components/schemas/Ref'
          description: |
            Reference to who created this Secret
        last_updated_by:
          $ref: '#/components/schemas/Ref'
          description: |
            Reference to who created this Secret
        vault:
          $ref: '#/components/schemas/Ref'
          description: |
            Reference to the vault the secret is stored in
        vault_name:
          description: |
            Name of the vault the secret is stored in
          type: string
    Ref:
      type: object
      properties:
        id:
          description: |
            a resource identifier
          type: string
        uri:
          description: |
            a uri for locating a resource
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Delete a specific vault secret by its unique identifier, permanently removing the stored value.

# Delete



## OpenAPI

````yaml delete /vault_secrets/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /vault_secrets/{id}:
    delete:
      tags:
        - Secrets
      summary: Delete
      description: |
        Delete a Secret
      operationId: SecretsDelete
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            a resource identifier
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: |
            Delete a Secret
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

> ## Documentation Index
> Fetch the complete documentation index at: https://ngrok.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

> Update an existing vault secret with a new value or modify its metadata.

# Update



## OpenAPI

````yaml patch /vault_secrets/{id}
openapi: 3.0.0
info:
  title: ngrok OpenAPI
  version: 1.0.0
servers:
  - url: https://api.ngrok.com
security:
  - authentication: []
paths:
  /vault_secrets/{id}:
    patch:
      tags:
        - Secrets
      summary: Update
      description: |
        Update an existing Secret by ID
      operationId: SecretsUpdate
      parameters:
        - $ref: '#/components/parameters/ngrokVersion'
        - name: id
          description: |
            identifier for Secret
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SecretUpdate'
      responses:
        '200':
          description: |
            Update an existing Secret by ID
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Secret'
components:
  parameters:
    ngrokVersion:
      name: ngrok-version
      in: header
      required: true
      schema:
        type: integer
        default: 2
  schemas:
    SecretUpdate:
      type: object
      properties:
        id:
          description: |
            identifier for Secret
          type: string
        name:
          description: |
            Name of secret
          type: string
        value:
          description: |
            Value of secret
          type: string
        metadata:
          description: |
            Arbitrary user-defined metadata for this Secret
          type: string
        description:
          description: |
            description of Secret
          type: string
    Secret:
      type: object
      properties:
        id:
          description: |
            identifier for Secret
          type: string
        uri:
          description: |
            URI of this Secret API resource
          type: string
        created_at:
          description: |
            Timestamp when the Secret was created (RFC 3339 format)
          type: string
        updated_at:
          description: |
            Timestamp when the Secret was last updated (RFC 3339 format)
          type: string
        name:
          description: |
            Name of secret
          type: string
        description:
          description: |
            description of Secret
          type: string
        metadata:
          description: |
            Arbitrary user-defined metadata for this Secret
          type: string
        created_by:
          $ref: '#/components/schemas/Ref'
          description: |
            Reference to who created this Secret
        last_updated_by:
          $ref: '#/components/schemas/Ref'
          description: |
            Reference to who created this Secret
        vault:
          $ref: '#/components/schemas/Ref'
          description: |
            Reference to the vault the secret is stored in
        vault_name:
          description: |
            Name of the vault the secret is stored in
          type: string
    Ref:
      type: object
      properties:
        id:
          description: |
            a resource identifier
          type: string
        uri:
          description: |
            a uri for locating a resource
          type: string
  securitySchemes:
    authentication:
      type: http
      scheme: bearer

````

Built with [Mintlify](https://mintlify.com).

