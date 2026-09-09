#!/usr/bin/env python3
"""Run the frozen SANER protocol once. This file performs no work without --execute."""
import argparse, datetime, hashlib, json, os, pathlib, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent
PROTOCOL = ROOT / "protocol"

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-lock", type=pathlib.Path, required=True)
    parser.add_argument("--run-id", help="unique output name; defaults to UTC timestamp")
    parser.add_argument("--execute", action="store_true", help="required safety gate")
    parser.add_argument("--with-4node-extension", action="store_true", help="also run the separately reported npm -> npm -> Docker -> Docker extension")
    args = parser.parse_args()
    lock = json.loads(args.release_lock.read_text())
    required = ("dispat_version", "dispat_version_output", "dispat_image", "dispat_binary_sha256", "runner_image", "runner_os", "runner_architecture")
    if any(not lock.get(k) or "REQUIRED" in lock[k] for k in required):
        raise SystemExit("release lock is incomplete")
    if not re.fullmatch(r"[0-9a-f]{64}", lock["dispat_binary_sha256"]):
        raise SystemExit("dispat_binary_sha256 must be 64 lowercase hexadecimal characters")
    if not re.fullmatch(r"[^@\s]+@sha256:[0-9a-f]{64}",lock["dispat_image"]):
        raise SystemExit("dispat_image must be immutable repository@sha256:... reference")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", lock["runner_image"]):
        raise SystemExit("runner_image must be the immutable local sha256 image ID")
    expected_version_output='dispat '+lock['dispat_version']+' ('+lock['runner_os']+'_'+lock['runner_architecture']+')'
    if lock['dispat_version_output'] != expected_version_output:
        raise SystemExit('dispat_version_output must exactly match locked version and platform: '+expected_version_output)
    manifest=json.loads((ROOT/'protocol-sha256.json').read_text())
    source_files=sorted(p for p in PROTOCOL.rglob('*') if p.is_file())
    observed_manifest={str(p.relative_to(PROTOCOL)):sha256(p) for p in source_files}
    if observed_manifest != manifest:
        missing=sorted(set(manifest)-set(observed_manifest));extra=sorted(set(observed_manifest)-set(manifest));changed=sorted(k for k in set(manifest)&set(observed_manifest) if manifest[k]!=observed_manifest[k])
        raise SystemExit('frozen protocol mismatch: '+json.dumps({'missing':missing,'extra':extra,'changed':changed}))
    run_id = args.run_id or datetime.datetime.now(datetime.timezone.utc).strftime("run-%Y%m%dT%H%M%SZ")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", run_id):
        raise SystemExit("invalid run id")
    destination = ROOT / "runs" / run_id
    if destination.exists():
        raise SystemExit("refusing to overwrite " + str(destination))
    if not args.execute:
        print(json.dumps({"status":"READY_NOT_EXECUTED", "destination":str(destination), "lock":lock}, indent=2))
        return

    destination.mkdir(parents=True)
    work = destination / "work"
    shutil.copytree(PROTOCOL, work)
    files = sorted(p for p in work.rglob("*") if p.is_file())
    provenance = {
        "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "release_lock": lock,
        "protocol_sha256": {str(p.relative_to(work)): sha256(p) for p in files},
        "frozen_protocol_manifest": "protocol-sha256.json",
        "campaign_driver_sha256": sha256(ROOT/"execute.py"),
        "protocol_manifest_sha256": sha256(ROOT/"protocol-sha256.json"),
        "runner_dockerfile_sha256": sha256(ROOT/"docker"/"Dockerfile"),
        "runner_apk_lock_sha256": sha256(ROOT/"docker"/"apk.lock"),
        "argv": sys.argv,
        "status": "RUNNING",
        "stages": [],
    }
    provenance_path=destination / "provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
    def run_stage(name, command, allowed=(0,)):
        started=datetime.datetime.now(datetime.timezone.utc).isoformat()
        print("+", " ".join(map(str,command)), flush=True)
        try:
         with (destination/(name+'.log')).open('w') as log:
            result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        except BaseException as exc:
         provenance['stages'].append({'name':name,'started_utc':started,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':None,'status':'SPAWN_OR_INTERRUPT_FAILURE','error':{'type':type(exc).__name__,'message':str(exc)},'allowed_exit_codes':list(allowed)})
         provenance_path.write_text(json.dumps(provenance,indent=2)+'\n')
         raise
        status='PASS' if result.returncode in allowed else 'FAIL'
        provenance['stages'].append({'name':name,'started_utc':started,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':result.returncode,'status':status,'allowed_exit_codes':list(allowed)})
        provenance_path.write_text(json.dumps(provenance,indent=2)+'\n')
        if result.returncode not in allowed:raise RuntimeError(name+' exited '+str(result.returncode))
        return result
    failure=None
    try:
     inspect_started=datetime.datetime.now(datetime.timezone.utc).isoformat()
     inspect_command=["docker", "image", "inspect", lock["runner_image"], "--format", "{{json .}}"]
     try:
      inspect_result=subprocess.run(inspect_command,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
     except BaseException as exc:
      provenance['stages'].append({'name':'runner-image-inspect','started_utc':inspect_started,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':None,'status':'SPAWN_OR_INTERRUPT_FAILURE','error':{'type':type(exc).__name__,'message':str(exc)},'allowed_exit_codes':[0]})
      provenance_path.write_text(json.dumps(provenance,indent=2)+'\n');raise
     provenance['stages'].append({'name':'runner-image-inspect','started_utc':inspect_started,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':inspect_result.returncode,'status':'PASS' if inspect_result.returncode==0 else 'FAIL','allowed_exit_codes':[0]})
     (destination/'runner-image-inspect.log').write_text(inspect_result.stdout)
     provenance_path.write_text(json.dumps(provenance,indent=2)+'\n')
     if inspect_result.returncode:raise RuntimeError('runner-image-inspect exited '+str(inspect_result.returncode))
     inspected=json.loads(inspect_result.stdout)
     labels=inspected.get('Config',{}).get('Labels') or {}
     if inspected.get('Id')!=lock['runner_image']:raise RuntimeError('runner image ID does not match lock')
     if inspected.get('Os')!=lock['runner_os'] or inspected.get('Architecture')!=lock['runner_architecture']:raise RuntimeError('runner platform does not match lock')
     if labels.get('org.dispat.research.source-image')!=lock['dispat_image']:raise RuntimeError('runner source-image label does not match released image digest')
     (destination / "runner-image.json").write_text(inspect_result.stdout)
     base = ["docker", "run", "--rm", "--network", "none",
            "-e", "GIT_CONFIG_COUNT=1", "-e", "GIT_CONFIG_KEY_0=init.defaultBranch", "-e", "GIT_CONFIG_VALUE_0=main",
            "-e", "GIT_AUTHOR_NAME=Experiment", "-e", "GIT_AUTHOR_EMAIL=experiment@example.invalid",
            "-e", "GIT_COMMITTER_NAME=Experiment", "-e", "GIT_COMMITTER_EMAIL=experiment@example.invalid",
            "-e", "DISPAT_EXPECTED_VERSION=" + lock["dispat_version"],
            "-e", "DISPAT_EXPECTED_VERSION_OUTPUT=" + lock["dispat_version_output"],
            "-e", "DISPAT_EXPECTED_SHA256=" + lock["dispat_binary_sha256"],
            "--cpus", "2", "--memory", "4g", "--tmpfs", "/workspaces:rw,size=1g", "-e", "TMPDIR=/workspaces",
            "-v", str(work / "harness") + ":/exp:ro", "-v", str(work) + ":/results", "-w", "/exp", lock["runner_image"]]
     stages = [
        ("release-identity-gate", ["sh", "-c", "test \"$(sha256sum /usr/local/bin/dispat | cut -d ' ' -f1)\" = \"$DISPAT_EXPECTED_SHA256\" && test \"$(dispat --version | tail -n 1)\" = \"$DISPAT_EXPECTED_VERSION_OUTPUT\""]),
        ("binary-provenance", ["sh", "-c", "dispat --version && sha256sum /usr/local/bin/dispat && python3 --version && node --version && npm --version && git --version && docker --version"]),
        ("parser-gate", ["sh", "e1/gate0.sh"]),
        ("golden-gate", ["python3", "e1/golden_test.py"]),
        ("core-holdout", ["python3", "e1/run.py", "--profile", "core", "--seed0", "90001", "--n", "300", "--workers", "2", "--out", "/results/core"]),
    ]
     (work / "core").mkdir(); (work / "recovery").mkdir()
     for name, stage in stages:
        run_stage(name,base+stage,(0,1) if name=='core-holdout' else (0,))
     run_stage('core-verification',base+["python3","/results/verify-core.py","/results/core",lock['dispat_version']])
     run_stage('recovery-holdout',base+["python3", "/results/recovery-holdout.py"])
     mixed = ["docker", "run", "--rm", "--name", "saner-next-release-mixed", "--cpus", "2", "--memory", "4g",
             "-e", "DISPAT_EXPECTED_VERSION=" + lock["dispat_version"], "-e", "DISPAT_EXPECTED_VERSION_OUTPUT=" + lock["dispat_version_output"], "-e", "DISPAT_EXPECTED_SHA256=" + lock["dispat_binary_sha256"],
             "-v", "/var/run/docker.sock:/var/run/docker.sock", "-v", str(work) + ":" + str(work), "-w", str(work), lock["runner_image"],
             "python3", str(work / "mixed-docker/run.py")]
     run_stage('mixed-docker',mixed)
     if args.with_4node_extension:
        mixed4 = mixed.copy()
        mixed4[mixed4.index("saner-next-release-mixed")] = "saner-next-release-mixed-4node"
        mixed4[-1] = str(work / "mixed-4node/run.py")
        run_stage('mixed-4node',mixed4)
     run_stage('integration',base+["python3", "/results/integration/run.py"])
     run_stage('recovery-verification',base+["python3", "/results/verify-recovery.py"])
     mixed_runs = sorted((work / "mixed-docker").glob("run-*"))
     if len(mixed_runs) != 1:
        raise RuntimeError("expected exactly one mixed run")
     run_stage('mixed-docker-verification',base+["python3", "/results/mixed-docker/verify.py", "/results/mixed-docker/" + mixed_runs[0].name])
     if args.with_4node_extension:
        mixed4_runs = sorted((work / "mixed-4node").glob("run-*"))
        if len(mixed4_runs) != 1:
            raise RuntimeError("expected exactly one four-node mixed run")
        run_stage('mixed-4node-verification',base+["python3", "/results/mixed-4node/verify.py", "/results/mixed-4node/" + mixed4_runs[0].name])
    except BaseException as exc:
     failure={'type':type(exc).__name__,'message':str(exc)}
     raise
    finally:
     provenance['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
     provenance['status']='FAILED' if failure else 'COMPLETE'
     if failure:provenance['failure']=failure
     provenance_path.write_text(json.dumps(provenance,indent=2)+'\n')
    (destination / "COMPLETE").write_text(provenance['completed_utc'] + "\n")

if __name__ == "__main__":
    main()
