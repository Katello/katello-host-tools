from __future__ import absolute_import


from katello.agent.pulp.libdnf import *


def test():
    from dnf.cli.main import main as cli
    cli(['install', 'ksh'])


def test_pattern():
    p = Pattern(name='jeff', version='1', arch='x68', release='2')
    print(p)


def test_packages(*pattern):
    names = pattern or ['bmake', 'mk-files']
    print('\n\nBegin')
    package = Package()
    log.info('\nInstalled [%s]: %s', names, package.install(names))
    names = [n.split('-', 1)[0] for n in names]
    log.info('\n\nUpdated [%s]: %s', names, package.update(names))
    log.info('\n\nUninstall [%s]: %s', names, package.uninstall(names))
    print('\nEnd')


def test_packages2(*pattern):
    print('\n\nBegin')
    package = Package()
    log.info('\nInstalled %s:\n%s', [str(p) for p in pattern], package.install(pattern))
    for p in pattern:
        p.version = ''
        p.release = ''
    log.info('\n\nUpdated %s:\n%s', [str(p) for p in pattern], package.update(pattern))
    log.info('\n\nUninstall %s: \n%s', [str(p) for p in pattern], package.uninstall(pattern))
    print('\nEnd')


def test_groups():
    names = ['Pulp Consumer']
    print('\nBegin')
    g = PackageGroup()
    log.info('Installed (group) %s', g.install(names))
    log.info('Uninstall (group) %s', g.uninstall(names))
    print('\nEnd')


def test_advisories():
    with LibDnf() as dnf:
        advisories = dnf.list_advisories()
        for ad in advisories:
            print('Ad: {}'.format(ad.id))
            for p in ad.packages:
                print('\t{}'.format(p.name))
        print('total: {}'.format(len(advisories)))


def test_applicable_advisories():
    with LibDnf() as dnf:
        advisories = dnf.applicable_advisories()
        for ad, packages in advisories:
            print('Ad: {}'.format(ad.id))
            for p in sorted(packages):
                print('\t{}'.format(p))
        print('total: {}'.format(len(advisories)))


def test_advisory_update():
    print('\nBegin')
    p = Package()
    log.info('Ad-Update: %s', p.update(advisories=['FEDORA-2017-de8a421dcd']))
    print('\nEnd')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    test_pattern()
    # test_packages()
    test_packages2(
        Pattern(name='walrus', version='0.71', release='1'),
        Pattern(name='zsh')
    )
    # test_applicable_advisories()
    # test_pattern()
    # test_advisories()
    # test_advisory_update()
