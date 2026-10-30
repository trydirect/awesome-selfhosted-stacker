# Marketplace descriptions: what to write

Every project can carry listing metadata in its `stacker.yml` under
`marketplace:`. `stacker submit` ships it to the TryDirect marketplace, and
the template page renders `long_description` as markdown.

The listing is read by **buyers deploying from the web UI**, not by developers
working in this repo. A description copied from the project's `README.md`
("git clone …", `generate-secrets.sh`, `stacker deploy`) describes the wrong
product: the buyer never runs those commands. Write for the person clicking
**Deploy** on try.direct.

## Structure (in this order)

1. **One or two sentences**: what the product is and why someone wants it
   self-hosted ("Self-hosted Firebase alternative: Postgres, auth, realtime...").
2. **What the deploy does**: TryDirect provisions the server, wires the
   services, generates credentials. Reassure: no shared state, no secrets in
   the image.
3. **What's included**: the service table (Service | Port | Description).
4. **What you configure**: only what the buyer actually types in the deploy
   form (`install.inputs`, `mutability: provided/editable` fields), e.g. the
   `commonDomain`. Everything `mutability: generated` is created for them, so
   say that instead of listing it.
5. **Use it for**: 2-4 concrete use cases.
6. **Requirements**: server size (count the services; ~1 GB RAM each for
   JVM/DB-heavy ones), DNS for the domain, any external account needed.
7. **Alternative: deploy with the Stacker CLI** *(optional, last)*: the
   `git clone` / `generate-secrets.sh` / `stacker deploy` recipe stays here as
   a secondary path for developers. It must never be the main content.

## Rules

- **Never use the em-dash character `—` (or `–`) anywhere in listing copy**:
  not in headings, not in descriptions, not in table cells, not in the short
  description. Use a colon, comma or parentheses instead. Reviewers and
  automated checks reject the character.
- Long description: 100-5000 characters of markdown (tables, code fences and
  links all render). Short description: 20-200 characters, one sentence.
- Buyer voice, present tense: "Deploy from this page...", "You configure...".
  Not: "Clone the repo...", "Run the script...".
- Describe this deployment, not upstream's marketing copy: name the actual
  services and ports from this project's `stacker.yml`.
- Never mention generated values; say they are generated per deployment.
- `no_secrets_confirmation: true` is a claim that no credentials are embedded
  in the stack. Only set it when `config_contract` marks secrets `generated`
  or the stack has none.

## Template

````yaml
marketplace:
  publish: true
  display_name: "<Product Name>"
  short_description: "<one sentence: what it is, deployed where>"
  long_description: |
    **<what it is in one line>**: <what the buyer gets>.

    Deploy from this page: TryDirect provisions the server, starts the
    services, generates every credential and wires <gateway/proxy> in front.

    ## What's included

    | Service | Port | Description |
    | ------- | ---- | ----------- |
    | ... | ... | ... |

    ## What you configure

    - **Domain** (`commonDomain`): ...
    - <other form fields only>

    Everything else is generated per deployment.

    ## Use it for

    - ...

    ## Requirements

    - A cloud account connected to TryDirect (or your own server)
    - <RAM/disk guidance from the service count>
    - A DNS record for your domain

    ## Alternative: deploy with the Stacker CLI

    ```bash
    git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
    cd awesome-selfhosted-stacker/stacker-projects/<name>
    cp .env.example .env
    ./scripts/generate-secrets.sh
    stacker deploy --target cloud --key htz-0
    ```
  category: <existing category code>
  tags: [<product>, <tech>, <use-case>]
  support_url: https://github.com/trydirect/awesome-selfhosted-stacker/tree/main/stacker-projects/<name>
  no_secrets_confirmation: true
````

Reference implementation: `stacker-projects/supabase/stacker.yml`.

CLI flags override these values when present
(`stacker submit --description ... --long-description ...`), so a one-off
rewrite can also be done without editing `stacker.yml`.

---

## Vendor assets policy

### Logos and avatars

Vendor logos and avatars **must be hosted on TryDirect** (`try.direct` domain).
External URLs (e.g. `https://example.com/logo.png`) are not allowed because:

- **Broken links** - external domains can expire, change, or return 404
- **Privacy** - third-party requests leak visitor IPs and referrers
- **Bandwidth theft** - hotlinking consumes the vendor's (or victim's) bandwidth
- **Security** - external images can be replaced with malicious content after approval

**Upload your logo through the vendor dashboard** instead of referencing an
external URL. The platform stores it on `try.direct` and serves it from there.

### Stack screenshots and diagrams

The same rule applies to any image embedded in `long_description`: prefer text
descriptions, service tables, and CLI recipes over external image links.
