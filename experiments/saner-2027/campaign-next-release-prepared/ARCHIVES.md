# Retained campaign records

Each finished attempt keeps its original provenance, stage logs, outcome status, and a complete `work.tar.gz` archive. The archive includes generated repositories and their `.git` metadata, configuration, registry observations, OCI artifacts, event traces, and verifier inputs. `ARCHIVE.json` records its SHA-256, size, and the count of regular files checked byte-for-byte against the retained local work tree. Failed attempts remain failed and have no COMPLETE marker.

To inspect a fresh copy, first verify the archive against `ARCHIVE.json`, then extract it in an empty directory:

```sh
tar -xzf /absolute/path/to/attempt/work.tar.gz -C /empty/review-directory
```

Do not overwrite a running or retained work tree. Local work directories stay available but are ignored by Git so disposable nested repositories are not accidentally committed as gitlinks. The complete archives, rather than those gitlinks, provide the recorded evidence. The paper uses only the explicitly identified final campaign; previous attempts and earlier-version campaigns are never pooled into its sample counts.
