"""Create a source ZIP without Git history, ignored data, or the local environment."""
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def main():
    result = subprocess.check_output(
        ['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT
    )
    paths = sorted(set(result.decode('utf-8').split('\0')) - {''})
    output = ROOT / '.release' / 'MediGo-source.zip'
    output.parent.mkdir(exist_ok=True)
    count = 0
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in paths:
            path = ROOT / name
            # Defense in depth if generated files are accidentally tracked again.
            if any(part in {'.git', '.venv', 'venv', 'media', 'static_collected', '__pycache__', '.release'} for part in path.relative_to(ROOT).parts):
                continue
            if (path.name.startswith('.env') and path.name != '.env.example') or path.suffix in {'.pem', '.key', '.sqlite3', '.sql', '.dump'}:
                continue
            if path.is_file() and not path.is_symlink():
                archive.write(path, 'MediGo/' + name)
                count += 1
    print(f'Exported {count} source files to {output}')


if __name__ == '__main__':
    main()
