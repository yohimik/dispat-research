#!/usr/bin/env python3
"""Add the llvm-aarch64 package and the cheap bundle to the orchestrator's
untracked root configurations (they travel in snapshots and are copied to the
baseline clone)."""
for p in ('dispat.gce.yaml', 'dispat.local.yaml'):
    t = open(p).read()
    if 'llvm-aarch64' not in t:
        t = t.replace('  LLVM_TOOLCHAIN_PROVIDERS: "llvm,lld,polly"\n',
                      '  LLVM_TOOLCHAIN_PROVIDERS: "llvm,lld,polly"\n  LLVM_BUNDLE_COMPRESSION: none\n', 1)
        t = t.replace('  lld:\n    $ref: ./.ci/dispat/packages/lld.yaml\n',
                      '  llvm-aarch64:\n    $ref: ./.ci/dispat/packages/llvm-aarch64.yaml\n'
                      '    buildOutputs: [_dispat/install, _dispat/build-info.json]\n'
                      '  lld:\n    $ref: ./.ci/dispat/packages/lld.yaml\n', 1)
        open(p, 'w').write(t)
    t = open(p).read()
    # The bundle is built and published on the orchestrator's own checkout; it
    # declares no outputs there, so nothing of its 1.85 GB tar is captured.
    t = t.replace('    buildOutputs: [_dispat/dist, _dispat/build-info.json]\n', '', 1)
    open(p, 'w').write(t)
    print(p, 'aarch64' in t, 'BUNDLE' in t, '_dispat/dist' not in t)
