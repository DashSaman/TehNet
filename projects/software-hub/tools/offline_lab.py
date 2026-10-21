"""Clean root extraction for the isolated no-swap laboratory, not a web route."""
from pathlib import Path,PurePosixPath
import posixpath,tarfile

def extract_clean_root(archive,destination):
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    expanded=0;count=0
    def root_filter(member,path):
        nonlocal expanded,count
        count+=1;expanded+=member.size if member.isfile() else 0
        if count>60000 or expanded>512*1024**2:raise tarfile.FilterError('Rootfs extraction cap')
        if member.name.startswith('/') or '..' in PurePosixPath(member.name).parts:raise tarfile.FilterError('Rootfs member escape')
        # Ubuntu alternatives use absolute links relative to its future chroot.
        # Materialize equivalent relative links, then retain Python's data filter.
        if member.issym() and member.linkname.startswith('/'):
            member=member.replace(linkname=posixpath.relpath(member.linkname.lstrip('/'),posixpath.dirname(member.name) or '.'))
        filtered=tarfile.data_filter(member,path)
        if filtered is not None and filtered.isdir():filtered=filtered.replace(mode=member.mode&0o1777)
        return filtered
    with tarfile.open(archive) as bundle:bundle.extractall(destination,filter=root_filter)
