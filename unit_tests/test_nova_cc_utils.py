# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import OrderedDict
from mock import patch, MagicMock, call, ANY

from test_utils import (
    CharmTestCase,
    get_default_config,
    patch_open,
)

__default_config = get_default_config()

with patch('charmhelpers.core.hookenv.config') as config:
    with patch('charmhelpers.contrib.openstack.utils.get_os_codename_package'):  # noqa
        # this makes the config behave more similar to the real config()
        config.side_effect = lambda k: __default_config[k]

        import nova_cc_utils as utils

TO_PATCH = [
    'apt_update',
    'apt_upgrade',
    'apt_install',
    'cmd_all_services',
    'config',
    'configure_installation_source',
    'disable_policy_rcd',
    'is_leader',
    'lsb_release',
    'enable_policy_rcd',
    'enable_services',
    'get_os_codename_install_source',
    'git_src_dir',
    'git_pip_venv_dir',
    'log',
    'os_release',
    'peer_store',
    'pip_install',
    'register_configs',
    'relation_ids',
    'remote_unit',
    'render',
    '_save_script_rc',
    'service_start',
    'services',
    'service_running',
    'service_stop',
    'related_units',
    'local_unit',
    'relation_get',
    'os_application_version_set',
    'token_cache_pkgs',
    'enable_memcache',
    'is_relation_made',
]

SCRIPTRC_ENV_VARS = {
    'OPENSTACK_PORT_MCASTPORT': 5404,
    'OPENSTACK_SERVICE_API_EC2': 'nova-api-ec2',
    'OPENSTACK_SERVICE_API_OS_COMPUTE': 'nova-api-os-compute',
    'OPENSTACK_SERVICE_CERT': 'nova-cert',
    'OPENSTACK_SERVICE_CONDUCTOR': 'nova-conductor',
    'OPENSTACK_SERVICE_OBJECTSTORE': 'nova-objectstore',
    'OPENSTACK_SERVICE_SCHEDULER': 'nova-scheduler',
}


AUTHORIZED_KEYS = """
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC27Us7lSjCpa7bumXAgc nova-compute-1
ssh-rsa BBBBB3NzaC1yc2EBBBBDBQBBBBBBBQC27Us7lSjCpa7bumXBgc nova-compute-2
ssh-rsa CCCCB3NzaC1yc2ECCCCDCQCBCCCBCQC27Us7lSjCpa7bumXCgc nova-compute-3
"""

BASE_ENDPOINTS = {
    'ec2_admin_url': 'http://foohost.com:8773/services/Cloud',
    'ec2_internal_url': 'http://foohost.com:8773/services/Cloud',
    'ec2_public_url': 'http://foohost.com:8773/services/Cloud',
    'ec2_region': 'RegionOne',
    'ec2_service': 'ec2',
    'nova_admin_url': 'http://foohost.com:8774/v2/$(tenant_id)s',
    'nova_internal_url': 'http://foohost.com:8774/v2/$(tenant_id)s',
    'nova_public_url': 'http://foohost.com:8774/v2/$(tenant_id)s',
    'nova_region': 'RegionOne',
    'nova_service': 'nova',
    's3_admin_url': 'http://foohost.com:3333',
    's3_internal_url': 'http://foohost.com:3333',
    's3_public_url': 'http://foohost.com:3333',
    's3_region': 'RegionOne',
    's3_service': 's3'
}

# Restart map should be constructed such that API services restart
# before frontends (haproxy/apache) to avoid port conflicts.
RESTART_MAP_ICEHOUSE = OrderedDict([
    ('/etc/nova/nova.conf', [
        'nova-api-ec2', 'nova-api-os-compute', 'nova-objectstore',
        'nova-cert', 'nova-scheduler', 'nova-conductor'
    ]),
    ('/etc/nova/api-paste.ini', [
        'nova-api-ec2', 'nova-api-os-compute'
    ]),
    ('/etc/haproxy/haproxy.cfg', ['haproxy']),
    ('/etc/apache2/sites-available/openstack_https_frontend', ['apache2']),
])
RESTART_MAP_OCATA_ACTUAL = OrderedDict([
    ('/etc/nova/nova.conf', [
        'nova-api-ec2', 'nova-api-os-compute', 'nova-objectstore',
        'nova-cert', 'nova-scheduler', 'nova-conductor', 'apache2'
    ]),
    ('/etc/nova/api-paste.ini', [
        'nova-api-ec2', 'nova-api-os-compute', 'apache2'
    ]),
    ('/etc/haproxy/haproxy.cfg', ['haproxy']),
    ('/etc/apache2/sites-available/openstack_https_frontend', ['apache2']),
    ('/etc/apache2/sites-enabled/wsgi-openstack-api.conf', ['apache2']),
])
RESTART_MAP_OCATA_BASE = OrderedDict([
    ('/etc/nova/nova.conf', [
        'nova-api-ec2', 'nova-api-os-compute', 'nova-placement-api',
        'nova-objectstore', 'nova-cert', 'nova-scheduler', 'nova-conductor'
    ]),
    ('/etc/nova/api-paste.ini', [
        'nova-api-ec2', 'nova-api-os-compute', 'nova-placement-api'
    ]),
    ('/etc/haproxy/haproxy.cfg', ['haproxy']),
    ('/etc/apache2/sites-available/openstack_https_frontend', ['apache2'])
])


DPKG_OPTS = [
    '--option', 'Dpkg::Options::=--force-confnew',
    '--option', 'Dpkg::Options::=--force-confdef',
]

GPG_PPA_CLOUD_ARCHIVE = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: SKS 1.1.6
Comment: Hostname: keyserver.ubuntu.com

mI0EUCEyTAEEAMuUxyfiegCCwn4J/c0nw5PUTSJdn5FqiUTq6iMfij65xf1vl0g/Mxqw0gfg
AJIsCDvO9N9dloLAwF6FUBMg5My7WyhRPTAKF505TKJboyX3Pp4J1fU1LV8QFVOp87vUh1Rz
B6GU7cSglhnbL85gmbJTllkzkb3h4Yw7W+edjcQ/ABEBAAG0K0xhdW5jaHBhZCBQUEEgZm9y
IFVidW50dSBDbG91ZCBBcmNoaXZlIFRlYW2IuAQTAQIAIgUCUCEyTAIbAwYLCQgHAwIGFQgC
CQoLBBYCAwECHgECF4AACgkQimhEop9oEE7kJAP/eTBgq3Mhbvo0d8elMOuqZx3nmU7gSyPh
ep0zYIRZ5TJWl/7PRtvp0CJA6N6ZywYTQ/4ANHhpibcHZkh8K0AzUvsGXnJRSFoJeqyDbD91
EhoO+4ZfHs2HvRBQEDZILMa2OyuB497E5Mmyua3HDEOrG2cVLllsUZzpTFCx8NgeMHk=
=jLBm
-----END PGP PUBLIC KEY BLOCK-----
"""

# ppa:ubuntu-cloud-archive/newton-staging
OS_ORIGIN_NEWTON_STAGING = """deb http://ppa.launchpad.net/\
ubuntu-cloud-archive/newton-staging/ubuntu xenial main
|
%s
""" % GPG_PPA_CLOUD_ARCHIVE

# ppa:ubuntu-cloud-archive/liberty-staging
OS_ORIGIN_LIBERTY_STAGING = """deb http://ppa.launchpad.net/\
ubuntu-cloud-archive/liberty-staging/ubuntu trusty main
|
%s
""" % GPG_PPA_CLOUD_ARCHIVE

openstack_origin_git = \
    """repositories:
         - {name: requirements,
            repository: 'git://git.openstack.org/openstack/requirements',
            branch: stable/juno}
         - {name: nova,
            repository: 'git://git.openstack.org/openstack/nova',
            branch: stable/juno}"""


class NovaCCUtilsTests(CharmTestCase):

    def setUp(self):
        super(NovaCCUtilsTests, self).setUp(utils, TO_PATCH)
        self.config.side_effect = self.test_config.get
        self.maxDiff = None

    def _resource_map(self):
        with patch('charmhelpers.contrib.openstack.context.'
                   'SubordinateConfigContext'):
            _map = utils.resource_map()
            return _map

    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    def test_resource_map_vmware(self, subcontext):
        fake_context = MagicMock()
        fake_context.return_value = {
            'sections': [],
            'services': ['nova-compute', 'nova-network'],

        }
        subcontext.return_value = fake_context
        self.os_release.return_value = 'diablo'
        _map = utils.resource_map()
        for s in ['nova-compute', 'nova-network']:
            self.assertIn(s, _map['/etc/nova/nova.conf']['services'])

    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    def test_resource_map_neutron_no_agent_installed(self, subcontext):
        self.os_release.return_value = 'diablo'
        self._resource_map()
        _map = utils.resource_map()
        services = []
        [services.extend(_map[c]['services'])for c in _map]
        for svc in services:
            self.assertNotIn('agent', svc)

    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    def test_resource_map_console_xvpvnc(self, subcontext):
        self.test_config.set('console-access-protocol', 'xvpvnc')
        self.os_release.return_value = 'diablo'
        self.relation_ids.return_value = []
        _map = utils.resource_map()
        console_services = ['nova-xvpvncproxy', 'nova-consoleauth']
        for service in console_services:
            self.assertIn(service, _map['/etc/nova/nova.conf']['services'])

    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    def test_resource_map_console_novnc(self, subcontext):
        self.test_config.set('console-access-protocol', 'novnc')
        self.relation_ids.return_value = []
        self.os_release.return_value = 'diablo'
        _map = utils.resource_map()
        console_services = ['nova-novncproxy', 'nova-consoleauth']
        for service in console_services:
            self.assertIn(service, _map['/etc/nova/nova.conf']['services'])

    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    def test_resource_map_console_vnc(self, subcontext):
        self.test_config.set('console-access-protocol', 'vnc')
        self.relation_ids.return_value = []
        self.os_release.return_value = 'diablo'
        _map = utils.resource_map()
        console_services = ['nova-novncproxy', 'nova-xvpvncproxy',
                            'nova-consoleauth']
        for service in console_services:
            self.assertIn(service, _map['/etc/nova/nova.conf']['services'])

    def test_console_attributes_none(self):
        self.test_config.set('console-access-protocol', None)
        _proto = utils.console_attributes('protocol')
        self.assertEquals(_proto, None)

    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    def test_resource_map_console_spice(self, subcontext):
        self.test_config.set('console-access-protocol', 'spice')
        self.os_release.return_value = 'diablo'
        self.relation_ids.return_value = []
        _map = utils.resource_map()
        console_services = ['nova-spiceproxy', 'nova-consoleauth']
        for service in console_services:
            self.assertIn(service, _map['/etc/nova/nova.conf']['services'])

    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    def test_resource_map_single_nova_consoleauth(self, subcontext):
        self.test_config.set('console-access-protocol', 'spice')
        self.test_config.set('single-nova-consoleauth', True)
        self.os_release.return_value = 'ocata'
        self.relation_ids.return_value = ['ha']
        _map = utils.resource_map()
        self.assertNotIn('nova-consoleauth',
                         _map['/etc/nova/nova.conf']['services'])

    @patch('charmhelpers.contrib.openstack.neutron.os_release')
    @patch('os.path.exists')
    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    def test_restart_map_api_before_frontends_icehouse(self, subcontext,
                                                       _exists, _os_release):
        _os_release.return_value = 'icehouse'
        self.os_release.return_value = 'icehouse'
        _exists.return_value = False
        self.enable_memcache.return_value = False
        self._resource_map()
        _map = utils.restart_map()
        self.assertIsInstance(_map, OrderedDict)
        self.assertEquals(_map, RESTART_MAP_ICEHOUSE)

    @patch('charmhelpers.contrib.openstack.neutron.os_release')
    @patch('os.path.exists')
    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    def test_restart_map_api_actual_ocata(self, subcontext,
                                          _exists, _os_release):
        _os_release.return_value = 'ocata'
        self.os_release.return_value = 'ocata'
        _exists.return_value = False
        self.enable_memcache.return_value = False
        self._resource_map()
        _map = utils.restart_map()
        self.assertIsInstance(_map, OrderedDict)
        self.assertEquals(_map, RESTART_MAP_OCATA_ACTUAL)

    @patch('charmhelpers.contrib.openstack.neutron.os_release')
    @patch('os.path.exists')
    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    def test_restart_map_api_ocata_base(self, subcontext,
                                        _exists, _os_release):
        _os_release.return_value = 'ocata'
        self.os_release.return_value = 'ocata'
        _exists.return_value = False
        self.enable_memcache.return_value = False
        self._resource_map()
        _map = utils.restart_map(actual_services=False)
        self.assertIsInstance(_map, OrderedDict)
        self.assertEquals(_map, RESTART_MAP_OCATA_BASE)

    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    @patch('os.path.exists')
    def test_restart_map_apache24(self, _exists, subcontext):
        _exists.return_Value = True
        self.os_release.return_value = 'diablo'
        self._resource_map()
        _map = utils.restart_map()
        self.assertTrue('/etc/apache2/sites-available/'
                        'openstack_https_frontend.conf' in _map)
        self.assertTrue('/etc/apache2/sites-available/'
                        'openstack_https_frontend' not in _map)

    def test_console_attributes_spice(self):
        _proto = utils.console_attributes('protocol', proto='spice')
        self.assertEquals(_proto, 'spice')

    def test_console_attributes_vnc(self):
        self.test_config.set('console-access-protocol', 'vnc')
        _proto = utils.console_attributes('protocol')
        _servs = utils.console_attributes('services')
        _pkgs = utils.console_attributes('packages')
        _proxy_page = utils.console_attributes('proxy-page')
        vnc_pkgs = ['nova-novncproxy', 'nova-xvpvncproxy', 'nova-consoleauth']
        vnc_servs = ['nova-novncproxy', 'nova-xvpvncproxy', 'nova-consoleauth']
        self.assertEquals(_proto, 'vnc')
        self.assertEquals(_servs, vnc_servs)
        self.assertEquals(_pkgs, vnc_pkgs)
        self.assertEquals(_proxy_page, None)

    def test_database_setup(self):
        self.relation_ids.return_value = ['shared-db:12']
        self.related_units.return_value = ['mysql/0']
        self.relation_get.return_value = (
            'nova-cloud-controller/0 nova-cloud-controller/1')
        self.local_unit.return_value = 'nova-cloud-controller/0'
        self.assertTrue(utils.database_setup(prefix='nova'))
        self.relation_get.assert_called_with('nova_allowed_units',
                                             rid='shared-db:12',
                                             unit='mysql/0')

    def test_database_not_setup(self):
        self.relation_ids.return_value = ['shared-db:12']
        self.related_units.return_value = ['mysql/0']
        self.relation_get.return_value = 'nova-cloud-controller/1'
        self.local_unit.return_value = 'nova-cloud-controller/0'
        self.assertFalse(utils.database_setup(prefix='nova'))
        self.relation_get.assert_called_with('nova_allowed_units',
                                             rid='shared-db:12',
                                             unit='mysql/0')
        self.relation_get.return_value = None
        self.assertFalse(utils.database_setup(prefix='nova'))
        self.relation_get.assert_called_with('nova_allowed_units',
                                             rid='shared-db:12',
                                             unit='mysql/0')

    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    @patch.object(utils, 'git_install_requested')
    def test_determine_packages_console(self, git_requested, subcontext):
        git_requested.return_value = False
        self.test_config.set('console-access-protocol', 'spice')
        self.relation_ids.return_value = []
        self.os_release.return_value = 'diablo'
        pkgs = utils.determine_packages()
        console_pkgs = ['nova-spiceproxy', 'nova-consoleauth']
        for console_pkg in console_pkgs:
            self.assertIn(console_pkg, pkgs)

    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    @patch.object(utils, 'git_install_requested')
    def test_determine_packages_base_icehouse(self, git_requested, subcontext):
        git_requested.return_value = False
        self.relation_ids.return_value = []
        self.os_release.return_value = 'icehouse'
        self.token_cache_pkgs.return_value = []
        self.enable_memcache.return_value = False
        pkgs = utils.determine_packages()
        ex = list(set(utils.BASE_PACKAGES + utils.BASE_SERVICES))
        # nova-placement-api is purposely dropped unless it's ocata
        ex.remove('nova-placement-api')
        self.assertEquals(ex, pkgs)

    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    @patch.object(utils, 'git_install_requested')
    def test_determine_packages_base_ocata(self, git_requested, subcontext):
        git_requested.return_value = False
        self.relation_ids.return_value = []
        self.os_release.return_value = 'ocata'
        self.token_cache_pkgs.return_value = []
        self.enable_memcache.return_value = False
        pkgs = utils.determine_packages()
        ex = list(set(utils.BASE_PACKAGES + utils.BASE_SERVICES))
        self.assertEquals(ex, pkgs)

    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    @patch.object(utils, 'git_install_requested')
    def test_determine_packages_serial_console(self,
                                               git_requested,
                                               subcontext):
        git_requested.return_value = False
        self.test_config.set('enable-serial-console', True)
        self.relation_ids.return_value = []
        self.os_release.return_value = 'juno'
        pkgs = utils.determine_packages()
        console_pkgs = ['nova-serialproxy', 'nova-consoleauth']
        for console_pkg in console_pkgs:
            self.assertIn(console_pkg, pkgs)

    @patch('charmhelpers.contrib.openstack.context.SubordinateConfigContext')
    @patch.object(utils, 'git_install_requested')
    def test_determine_packages_serial_console_icehouse(self,
                                                        git_requested,
                                                        subcontext):
        git_requested.return_value = False
        self.test_config.set('enable-serial-console', True)
        self.relation_ids.return_value = []
        self.os_release.return_value = 'icehouse'
        pkgs = utils.determine_packages()
        console_pkgs = ['nova-serialproxy', 'nova-consoleauth']
        for console_pkg in console_pkgs:
            self.assertNotIn(console_pkg, pkgs)

    @patch.object(utils, 'restart_map')
    def test_determine_ports(self, restart_map):
        restart_map.return_value = {
            '/etc/nova/nova.conf': ['nova-api-os-compute', 'nova-api-ec2'],
            '/etc/nova/api-paste.ini': ['nova-api-os-compute', 'nova-api-ec2'],
        }
        ports = utils.determine_ports()
        ex = [8773, 8774]
        self.assertEquals(ex, sorted(ports))

    def test_save_script_rc_base(self):
        self.relation_ids.return_value = []
        utils.save_script_rc()
        self._save_script_rc.called_with(**SCRIPTRC_ENV_VARS)

    @patch('charmhelpers.contrib.openstack.utils.lsb_release')
    def test_get_step_upgrade_source_target_liberty(self, lsb_release):
        self.lsb_release.return_value = {'DISTRIB_CODENAME': 'trusty'}
        lsb_release.return_value = {'DISTRIB_CODENAME': 'trusty'}
        self.get_os_codename_install_source.side_effect = self.originals[
            'get_os_codename_install_source']

        # icehouse -> liberty
        self.os_release.return_value = 'icehouse'
        self.assertEquals(
            utils.get_step_upgrade_source('cloud:trusty-liberty'),
            'cloud:trusty-kilo')

        # juno -> liberty
        self.os_release.return_value = 'juno'
        self.assertEquals(
            utils.get_step_upgrade_source('cloud:trusty-liberty'),
            'cloud:trusty-kilo')

        # kilo -> liberty
        self.os_release.return_value = 'kilo'
        with patch_open() as (_open, _file):
            self.assertEquals(
                utils.get_step_upgrade_source('cloud:trusty-liberty'),
                None)

    @patch('charmhelpers.contrib.openstack.utils.lsb_release')
    def test_get_setup_upgrade_source_target_newton(self, lsb_release):
        # mitaka -> newton
        self.lsb_release.return_value = {'DISTRIB_CODENAME': 'xenial'}
        lsb_release.return_value = {'DISTRIB_CODENAME': 'xenial'}
        self.os_release.return_value = 'mitaka'
        self.get_os_codename_install_source.side_effect = self.originals[
            'get_os_codename_install_source']

        step_src = utils.get_step_upgrade_source(OS_ORIGIN_NEWTON_STAGING)
        self.assertEqual(step_src, None)

    @patch('charmhelpers.contrib.openstack.utils.lsb_release')
    def test_get_setup_upgrade_source_target_liberty_with_mirror(self,
                                                                 lsb_release):
        # from icehouse to liberty using a raw deb repo
        self.lsb_release.return_value = {'DISTRIB_CODENAME': 'trusty'}
        lsb_release.return_value = {'DISTRIB_CODENAME': 'trusty'}
        self.get_os_codename_install_source.side_effect = self.originals[
            'get_os_codename_install_source']
        self.os_release.return_value = 'icehouse'
        step_src = utils.get_step_upgrade_source(OS_ORIGIN_LIBERTY_STAGING)
        self.assertEqual(step_src, 'cloud:trusty-kilo')

    @patch.object(utils, 'remove_known_host')
    @patch.object(utils, 'ssh_known_host_key')
    @patch('subprocess.check_output')
    def test_add_known_host_exists(self, check_output, host_key, rm):
        check_output.return_value = '|1|= fookey'
        host_key.return_value = '|1|= fookey'
        with patch_open() as (_open, _file):
            utils.add_known_host('foohost')
            self.assertFalse(rm.called)
            self.assertFalse(_file.write.called)

    @patch.object(utils, 'known_hosts')
    @patch.object(utils, 'remove_known_host')
    @patch.object(utils, 'ssh_known_host_key')
    @patch('subprocess.check_output')
    def test_add_known_host_exists_outdated(
            self, check_output, host_key, rm, known_hosts):
        check_output.return_value = '|1|= fookey'
        host_key.return_value = '|1|= fookey_old'
        with patch_open() as (_open, _file):
            utils.add_known_host('foohost', None, None)
            rm.assert_called_with('foohost', None, None)

    @patch.object(utils, 'known_hosts')
    @patch.object(utils, 'remove_known_host')
    @patch.object(utils, 'ssh_known_host_key')
    @patch('subprocess.check_output')
    def test_add_known_host_exists_added(
            self, check_output, host_key, rm, known_hosts):
        check_output.return_value = '|1|= fookey'
        host_key.return_value = None
        with patch_open() as (_open, _file):
            _file.write = MagicMock()
            utils.add_known_host('foohost')
            self.assertFalse(rm.called)
            _file.write.assert_called_with('|1|= fookey\n')

    @patch('__builtin__.open')
    @patch('os.mkdir')
    @patch('os.path.isdir')
    def test_ssh_directory_for_unit(self, isdir, mkdir, _open):
        self.remote_unit.return_value = 'nova-compute/0'
        isdir.return_value = False
        self.assertEquals(utils.ssh_directory_for_unit(),
                          '/etc/nova/compute_ssh/nova-compute')
        self.assertIn([
            call('/etc/nova/compute_ssh/nova-compute/authorized_keys', 'w'),
            call('/etc/nova/compute_ssh/nova-compute/known_hosts', 'w')
        ], _open.call_args_list)

    @patch.object(utils, 'ssh_directory_for_unit')
    def test_known_hosts(self, ssh_dir):
        ssh_dir.return_value = '/tmp/foo'
        self.assertEquals(utils.known_hosts(), '/tmp/foo/known_hosts')
        ssh_dir.assert_called_with(None, None)
        self.assertEquals(utils.known_hosts('bar'), '/tmp/foo/known_hosts')
        ssh_dir.assert_called_with('bar', None)

    @patch.object(utils, 'ssh_directory_for_unit')
    def test_authorized_keys(self, ssh_dir):
        ssh_dir.return_value = '/tmp/foo'
        self.assertEquals(utils.authorized_keys(), '/tmp/foo/authorized_keys')
        ssh_dir.assert_called_with(None, None)
        self.assertEquals(
            utils.authorized_keys('bar'),
            '/tmp/foo/authorized_keys')
        ssh_dir.assert_called_with('bar', None)

    @patch.object(utils, 'known_hosts')
    @patch('subprocess.check_call')
    def test_remove_host_key(self, check_call, known_hosts):
        known_hosts.return_value = '/tmp/known_hosts'
        utils.remove_known_host('foo')
        check_call.assert_called_with([
            'ssh-keygen', '-f', known_hosts(), '-R', 'foo'])

    @patch.object(utils, 'authorized_keys')
    def test_ssh_authorized_key_exists(self, keys):
        key = 'BBBBB3NzaC1yc2EBBBBDBQBBBBBBBQC27Us7lSjCpa7bumXBgc'
        with patch_open() as (_open, _file):
            _file.read.return_value = AUTHORIZED_KEYS
            self.assertTrue(utils.ssh_authorized_key_exists(key))

    @patch.object(utils, 'authorized_keys')
    def test_ssh_authorized_key_doesnt_exist(self, keys):
        key = ('xxxx')
        with patch_open() as (_open, _file):
            _file.read = MagicMock()
            _file.readreturn_value = AUTHORIZED_KEYS
            self.assertFalse(utils.ssh_authorized_key_exists(key))

    @patch.object(utils, 'known_hosts')
    @patch.object(utils, 'authorized_keys')
    @patch('os.path.isfile')
    def test_ssh_compute_remove(self, isfile,
                                auth_key, known_host):
        isfile.return_value = False

        removed_key = AUTHORIZED_KEYS.split('\n')[2]

        keys_removed = (
            "\nssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC27Us7lSjCpa7bumXAgc "
            "nova-compute-1\n"
            "ssh-rsa CCCCB3NzaC1yc2ECCCCDCQCBCCCBCQC27Us7lSjCpa7bumXCgc "
            "nova-compute-3\n"
        )
        isfile.return_value = True
        self.remote_unit.return_value = 'nova-compute/2'
        with patch_open() as (_open, _file):
            _file.readlines = MagicMock()
            _file.write = MagicMock()
            _file.readlines.return_value = AUTHORIZED_KEYS.split('\n')
            utils.ssh_compute_remove(removed_key)
            _file.write.assert_called_with(keys_removed)

    def test_determine_endpoints_base(self):
        self.relation_ids.return_value = []
        self.os_release.return_value = 'diablo'
        self.assertEquals(
            BASE_ENDPOINTS, utils.determine_endpoints('http://foohost.com',
                                                      'http://foohost.com',
                                                      'http://foohost.com'))

    @patch.object(utils, 'known_hosts')
    @patch('subprocess.check_output')
    def test_ssh_known_host_key(self, _check_output, _known_hosts):
        _known_hosts.return_value = '/foo/known_hosts'
        utils.ssh_known_host_key('test')
        _check_output.assert_called_with(
            ['ssh-keygen', '-f', '/foo/known_hosts',
             '-H', '-F', 'test'])
        _known_hosts.assert_called_with(None, None)
        utils.ssh_known_host_key('test', 'bar')
        _known_hosts.assert_called_with('bar', None)

    @patch.object(utils, 'known_hosts')
    @patch('subprocess.check_output')
    def test_ssh_known_host_key_bug1500589(self, _check_output, _known_hosts):
        """On precise ssh-keygen does not error if host not found in file. So
         check charm processes empty output properly"""
        _known_hosts.return_value = '/foo/known_hosts'
        _check_output.return_value = ''
        key = utils.ssh_known_host_key('test')
        self.assertEquals(key, None)

    @patch.object(utils, 'known_hosts')
    @patch('subprocess.check_call')
    def test_remove_known_host(self, _check_call, _known_hosts):
        _known_hosts.return_value = '/foo/known_hosts'
        utils.remove_known_host('test')
        _check_call.assert_called_with(
            ['ssh-keygen', '-f', '/foo/known_hosts',
             '-R', 'test'])
        _known_hosts.assert_called_with(None, None)
        utils.remove_known_host('test', 'bar')
        _known_hosts.assert_called_with('bar', None)

    @patch('subprocess.check_output')
    def test_migrate_nova_databases(self, check_output):
        "Migrate database with nova-manage"
        self.relation_ids.return_value = []
        self.os_release.return_value = 'diablo'
        utils.migrate_nova_databases()
        check_output.assert_called_with(['nova-manage', 'db', 'sync'])
        self.assertTrue(self.enable_services.called)
        self.cmd_all_services.assert_called_with('start')

    @patch('subprocess.check_output')
    def test_migrate_nova_databases_cluster(self, check_output):
        "Migrate database with nova-manage in a clustered env"
        self.relation_ids.return_value = ['cluster:1']
        self.os_release.return_value = 'diablo'
        utils.migrate_nova_databases()
        check_output.assert_called_with(['nova-manage', 'db', 'sync'])
        self.peer_store.assert_called_with('dbsync_state', 'complete')
        self.assertTrue(self.enable_services.called)
        self.cmd_all_services.assert_called_with('start')

    @patch('subprocess.check_output')
    def test_migrate_nova_databases_mitaka(self, check_output):
        "Migrate database with nova-manage in a clustered env"
        self.relation_ids.return_value = ['cluster:1']
        self.os_release.return_value = 'mitaka'
        utils.migrate_nova_databases()
        check_output.assert_has_calls([
            call(['nova-manage', 'api_db', 'sync']),
            call(['nova-manage', 'db', 'sync']),
        ])
        self.peer_store.assert_called_with('dbsync_state', 'complete')
        self.assertTrue(self.enable_services.called)
        self.cmd_all_services.assert_called_with('start')

    @patch('subprocess.call')
    @patch('subprocess.check_output')
    def test_migrate_nova_databases_ocata(self, check_output, mock_call):
        "Migrate database with nova-manage in a clustered env"
        self.is_relation_made.return_value = True
        self.relation_ids.return_value = ['cluster:1']
        self.os_release.return_value = 'ocata'
        utils.migrate_nova_databases()
        mock_call.assert_has_calls([
            call(['nova-manage', 'cell_v2', 'create_cell', '--name', 'cell1']),
        ])
        check_output.assert_has_calls([
            call(['nova-manage', 'api_db', 'sync']),
            call(['nova-manage', 'cell_v2', 'map_cell0']),
            call(['nova-manage', 'db', 'sync']),
            call(['nova-manage', 'cell_v2', 'list_cells']),
            ANY,
        ])
        self.peer_store.assert_called_with('dbsync_state', 'complete')
        self.assertTrue(self.enable_services.called)
        self.cmd_all_services.assert_called_with('start')

    @patch('subprocess.check_output')
    def test_migrate_nova_flavors(self, check_output):
        utils.migrate_nova_flavors()
        check_output.assert_called_with(
            ['nova-manage', 'db', 'migrate_flavor_data'])

    @patch.object(utils, 'get_step_upgrade_source')
    @patch.object(utils, 'migrate_nova_databases')
    @patch.object(utils, 'determine_packages')
    def test_upgrade_icehouse_juno(self, determine_packages,
                                   migrate_nova_databases,
                                   get_step_upgrade_source):
        "Simulate a call to do_openstack_upgrade() for icehouse->juno"
        self.test_config.set('openstack-origin', 'cloud:trusty-juno')
        get_step_upgrade_source.return_value = None
        self.os_release.return_value = 'icehouse'
        self.get_os_codename_install_source.return_value = 'juno'
        self.is_leader.return_value = True
        self.relation_ids.return_value = []
        utils.do_openstack_upgrade(self.register_configs())
        self.apt_update.assert_called_with(fatal=True)
        self.apt_upgrade.assert_called_with(options=DPKG_OPTS, fatal=True,
                                            dist=True)
        self.apt_install.assert_called_with(determine_packages(), fatal=True)
        self.register_configs.assert_called_with(release='juno')
        self.assertTrue(migrate_nova_databases.call_count, 1)

    @patch.object(utils, 'get_step_upgrade_source')
    @patch.object(utils, 'migrate_nova_databases')
    @patch.object(utils, 'determine_packages')
    def test_upgrade_juno_kilo(self, determine_packages,
                               migrate_nova_databases,
                               get_step_upgrade_source):
        "Simulate a call to do_openstack_upgrade() for juno->kilo"
        self.test_config.set('openstack-origin', 'cloud:trusty-kilo')
        get_step_upgrade_source.return_value = None
        self.os_release.return_value = 'juno'
        self.get_os_codename_install_source.return_value = 'kilo'
        self.is_leader.return_value = True
        self.relation_ids.return_value = []
        utils.do_openstack_upgrade(self.register_configs())
        self.apt_update.assert_called_with(fatal=True)
        self.apt_upgrade.assert_called_with(options=DPKG_OPTS, fatal=True,
                                            dist=True)
        self.apt_install.assert_called_with(determine_packages(), fatal=True)
        self.register_configs.assert_called_with(release='kilo')
        self.assertTrue(migrate_nova_databases.call_count, 1)

    @patch.object(utils, 'get_step_upgrade_source')
    @patch.object(utils, 'migrate_nova_flavors')
    @patch.object(utils, 'migrate_nova_databases')
    @patch.object(utils, 'determine_packages')
    def test_upgrade_kilo_liberty(self, determine_packages,
                                  migrate_nova_databases,
                                  migrate_nova_flavors,
                                  get_step_upgrade_source):
        "Simulate a call to do_openstack_upgrade() for kilo->liberty"
        self.test_config.set('openstack-origin', 'cloud:trusty-liberty')
        get_step_upgrade_source.return_value = None
        self.os_release.return_value = 'kilo'
        self.get_os_codename_install_source.return_value = 'liberty'
        self.is_leader.return_value = True
        self.relation_ids.return_value = []
        utils.do_openstack_upgrade(self.register_configs())
        self.apt_update.assert_called_with(fatal=True)
        self.apt_upgrade.assert_called_with(options=DPKG_OPTS, fatal=True,
                                            dist=True)
        self.apt_install.assert_called_with(determine_packages(), fatal=True)
        self.register_configs.assert_called_with(release='liberty')
        self.assertTrue(migrate_nova_flavors.call_count, 1)
        self.assertTrue(migrate_nova_databases.call_count, 1)

    @patch.object(utils, 'database_setup')
    @patch.object(utils, 'get_step_upgrade_source')
    @patch.object(utils, 'migrate_nova_databases')
    @patch.object(utils, 'determine_packages')
    def test_upgrade_liberty_mitaka(self, determine_packages,
                                    migrate_nova_databases,
                                    get_step_upgrade_source,
                                    database_setup):
        "Simulate a call to do_openstack_upgrade() for liberty->mitaka"
        self.test_config.set('openstack-origin', 'cloud:trusty-kilo')
        get_step_upgrade_source.return_value = None
        self.os_release.return_value = 'liberty'
        self.get_os_codename_install_source.return_value = 'mitaka'
        self.is_leader.return_value = True
        self.relation_ids.return_value = []
        database_setup.return_value = False
        utils.do_openstack_upgrade(self.register_configs())
        self.apt_update.assert_called_with(fatal=True)
        self.apt_upgrade.assert_called_with(options=DPKG_OPTS, fatal=True,
                                            dist=True)
        self.apt_install.assert_called_with(determine_packages(), fatal=True)
        self.register_configs.assert_called_with(release='mitaka')
        self.assertFalse(migrate_nova_databases.called)
        database_setup.assert_called_with(prefix='novaapi')

    def test_guard_map_nova(self):
        self.relation_ids.return_value = []
        self.os_release.return_value = 'icehouse'
        self.assertEqual(
            {'nova-api-ec2': ['identity-service', 'amqp', 'shared-db'],
             'nova-api-os-compute': ['identity-service', 'amqp', 'shared-db'],
             'nova-cert': ['identity-service', 'amqp', 'shared-db'],
             'nova-conductor': ['identity-service', 'amqp', 'shared-db'],
             'nova-objectstore': ['identity-service', 'amqp', 'shared-db'],
             'nova-placement-api': ['identity-service', 'amqp', 'shared-db'],
             'nova-scheduler': ['identity-service', 'amqp', 'shared-db']},
            utils.guard_map()
        )

    def test_guard_map_neutron(self):
        self.relation_ids.return_value = []
        self.os_release.return_value = 'icehouse'
        self.get_os_codename_install_source.return_value = 'icehouse'
        self.assertEqual(
            {'nova-api-ec2': ['identity-service', 'amqp', 'shared-db'],
             'nova-api-os-compute': ['identity-service', 'amqp', 'shared-db'],
             'nova-cert': ['identity-service', 'amqp', 'shared-db'],
             'nova-conductor': ['identity-service', 'amqp', 'shared-db'],
             'nova-objectstore': ['identity-service', 'amqp', 'shared-db'],
             'nova-placement-api': ['identity-service', 'amqp', 'shared-db'],
             'nova-scheduler': ['identity-service', 'amqp', 'shared-db'], },
            utils.guard_map()
        )
        self.os_release.return_value = 'mitaka'
        self.get_os_codename_install_source.return_value = 'mitaka'
        self.assertEqual(
            {'nova-api-os-compute': ['identity-service', 'amqp', 'shared-db'],
             'nova-cert': ['identity-service', 'amqp', 'shared-db'],
             'nova-conductor': ['identity-service', 'amqp', 'shared-db'],
             'nova-placement-api': ['identity-service', 'amqp', 'shared-db'],
             'nova-scheduler': ['identity-service', 'amqp', 'shared-db'], },
            utils.guard_map()
        )

    def test_guard_map_pgsql(self):
        self.relation_ids.return_value = ['pgsql:1']
        self.os_release.return_value = 'icehouse'
        self.assertEqual(
            {'nova-api-ec2': ['identity-service', 'amqp', 'pgsql-nova-db'],
             'nova-api-os-compute': ['identity-service', 'amqp',
                                     'pgsql-nova-db'],
             'nova-cert': ['identity-service', 'amqp', 'pgsql-nova-db'],
             'nova-conductor': ['identity-service', 'amqp', 'pgsql-nova-db'],
             'nova-objectstore': ['identity-service', 'amqp',
                                  'pgsql-nova-db'],
             'nova-placement-api': ['identity-service', 'amqp',
                                    'pgsql-nova-db'],
             'nova-scheduler': ['identity-service', 'amqp',
                                'pgsql-nova-db'], },
            utils.guard_map()
        )

    def test_service_guard_inactive(self):
        '''Ensure that if disabled, service guards nothing'''
        contexts = MagicMock()

        @utils.service_guard({'test': ['interfacea', 'interfaceb']},
                             contexts, False)
        def dummy_func():
            pass
        dummy_func()
        self.assertFalse(self.service_running.called)
        self.assertFalse(contexts.complete_contexts.called)

    def test_service_guard_active_guard(self):
        '''Ensure services with incomplete interfaces are stopped'''
        contexts = MagicMock()
        contexts.complete_contexts.return_value = ['interfacea']
        self.service_running.return_value = True

        @utils.service_guard({'test': ['interfacea', 'interfaceb']},
                             contexts, True)
        def dummy_func():
            pass
        dummy_func()
        self.service_running.assert_called_with('test')
        self.service_stop.assert_called_with('test')
        self.assertTrue(contexts.complete_contexts.called)

    def test_service_guard_active_release(self):
        '''Ensure services with complete interfaces are not stopped'''
        contexts = MagicMock()
        contexts.complete_contexts.return_value = ['interfacea',
                                                   'interfaceb']

        @utils.service_guard({'test': ['interfacea', 'interfaceb']},
                             contexts, True)
        def dummy_func():
            pass
        dummy_func()
        self.assertFalse(self.service_running.called)
        self.assertFalse(self.service_stop.called)
        self.assertTrue(contexts.complete_contexts.called)

    @patch.object(utils, 'git_install_requested')
    @patch.object(utils, 'git_clone_and_install')
    @patch.object(utils, 'git_post_install')
    @patch.object(utils, 'git_pre_install')
    def test_git_install(self, git_pre, git_post, git_clone_and_install,
                         git_requested):
        projects_yaml = openstack_origin_git
        git_requested.return_value = True
        utils.git_install(projects_yaml)
        self.assertTrue(git_pre.called)
        git_clone_and_install.assert_called_with(openstack_origin_git,
                                                 core_project='nova')
        self.assertTrue(git_post.called)

    @patch.object(utils, 'mkdir')
    @patch.object(utils, 'add_user_to_group')
    @patch.object(utils, 'add_group')
    @patch.object(utils, 'adduser')
    @patch('subprocess.check_call')
    def test_git_pre_install(self, check_call, adduser, add_group,
                             add_user_to_group, mkdir):
        utils.git_pre_install()
        expected = [
            call('nova', shell='/bin/bash', system_user=True),
            call('neutron', shell='/bin/bash', system_user=True),
        ]
        self.assertEquals(adduser.call_args_list, expected)
        check_call.assert_called_with(['usermod', '--home', '/var/lib/nova',
                                       'nova'])
        expected = [
            call('nova', system_group=True),
            call('neutron', system_group=True),
        ]
        self.assertEquals(add_group.call_args_list, expected)
        expected = [
            call('nova', 'nova'),
            call('neutron', 'neutron'),
        ]
        self.assertEquals(add_user_to_group.call_args_list, expected)
        expected = [
            call('/var/lib/nova', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/var/lib/nova/buckets', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/var/lib/nova/CA', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/var/lib/nova/CA/INTER', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/var/lib/nova/CA/newcerts', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/var/lib/nova/CA/private', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/var/lib/nova/CA/reqs', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/var/lib/nova/images', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/var/lib/nova/instances', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/var/lib/nova/keys', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/var/lib/nova/networks', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/var/lib/nova/tmp', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/var/lib/neutron', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/var/lib/neutron/lock', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/var/log/nova', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/etc/neutron', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/etc/neutron/plugins', owner='nova',
                 group='nova', perms=0755, force=False),
            call('/etc/neutron/plugins/ml2', owner='nova',
                 group='nova', perms=0755, force=False),
        ]
        self.assertEquals(mkdir.call_args_list, expected)

    @patch('os.listdir')
    @patch('os.path.join')
    @patch('os.path.exists')
    @patch('os.symlink')
    @patch('shutil.copytree')
    @patch('shutil.rmtree')
    def test_git_post_install_upstart(self, rmtree, copytree, symlink, exists,
                                      join, listdir):
        projects_yaml = openstack_origin_git
        join.return_value = 'joined-string'
        self.lsb_release.return_value = {'DISTRIB_RELEASE': '15.04'}
        self.git_pip_venv_dir.return_value = '/mnt/openstack-git/venv'
        self.os_release.return_value = 'diablo'
        utils.git_post_install(projects_yaml)
        expected = [
            call('joined-string', '/etc/nova'),
        ]
        copytree.assert_has_calls(expected)
        expected = [
            call('joined-string', '/usr/local/bin/nova-manage'),
            call('joined-string', '/usr/local/bin/nova-rootwrap'),
        ]

        nova_cc = 'nova-cloud-controller'
        nova_user = 'nova'
        start_dir = '/var/lib/nova'
        nova_conf = '/etc/nova/nova.conf'
        nova_ec2_api_context = {
            'service_description': 'Nova EC2 API server',
            'service_name': nova_cc,
            'user_name': nova_user,
            'start_dir': start_dir,
            'process_name': 'nova-api-ec2',
            'executable_name': 'joined-string',
            'config_files': [nova_conf],
        }
        nova_api_os_compute_context = {
            'service_description': 'Nova OpenStack Compute API server',
            'service_name': nova_cc,
            'user_name': nova_user,
            'start_dir': start_dir,
            'process_name': 'nova-api-os-compute',
            'executable_name': 'joined-string',
            'config_files': [nova_conf],
        }
        nova_cells_context = {
            'service_description': 'Nova cells',
            'service_name': nova_cc,
            'user_name': nova_user,
            'start_dir': start_dir,
            'process_name': 'nova-cells',
            'executable_name': 'joined-string',
            'config_files': [nova_conf],
        }
        nova_cert_context = {
            'service_description': 'Nova cert',
            'service_name': nova_cc,
            'user_name': nova_user,
            'start_dir': start_dir,
            'process_name': 'nova-cert',
            'executable_name': 'joined-string',
            'config_files': [nova_conf],
        }
        nova_conductor_context = {
            'service_description': 'Nova conductor',
            'service_name': nova_cc,
            'user_name': nova_user,
            'start_dir': start_dir,
            'process_name': 'nova-conductor',
            'executable_name': 'joined-string',
            'config_files': [nova_conf],
        }
        nova_consoleauth_context = {
            'service_description': 'Nova console auth',
            'service_name': nova_cc,
            'user_name': nova_user,
            'start_dir': start_dir,
            'process_name': 'nova-consoleauth',
            'executable_name': 'joined-string',
            'config_files': [nova_conf],
        }
        nova_console_context = {
            'service_description': 'Nova console',
            'service_name': nova_cc,
            'user_name': nova_user,
            'start_dir': start_dir,
            'process_name': 'nova-console',
            'executable_name': 'joined-string',
            'config_files': [nova_conf],
        }
        nova_novncproxy_context = {
            'service_description': 'Nova NoVNC proxy',
            'service_name': nova_cc,
            'user_name': nova_user,
            'start_dir': start_dir,
            'process_name': 'nova-novncproxy',
            'executable_name': 'joined-string',
            'config_files': [nova_conf],
        }
        nova_objectstore_context = {
            'service_description': 'Nova object store',
            'service_name': nova_cc,
            'user_name': nova_user,
            'start_dir': start_dir,
            'process_name': 'nova-objectstore',
            'executable_name': 'joined-string',
            'config_files': [nova_conf],
        }
        nova_scheduler_context = {
            'service_description': 'Nova scheduler',
            'service_name': nova_cc,
            'user_name': nova_user,
            'start_dir': start_dir,
            'process_name': 'nova-scheduler',
            'executable_name': 'joined-string',
            'config_files': [nova_conf],
        }
        nova_spiceproxy_context = {
            'service_description': 'Nova spice proxy',
            'service_name': nova_cc,
            'user_name': nova_user,
            'start_dir': start_dir,
            'process_name': 'nova-spicehtml5proxy',
            'executable_name': 'joined-string',
            'config_files': [nova_conf],
        }
        nova_xvpvncproxy_context = {
            'service_description': 'Nova XVPVNC proxy',
            'service_name': nova_cc,
            'user_name': nova_user,
            'start_dir': start_dir,
            'process_name': 'nova-xvpvncproxy',
            'executable_name': 'joined-string',
            'config_files': [nova_conf],
        }
        expected = [
            call('git/nova_sudoers', '/etc/sudoers.d/nova_sudoers',
                 {}, perms=0o440),
            call('git.upstart', '/etc/init/nova-api-ec2.conf',
                 nova_ec2_api_context, perms=0o644,
                 templates_dir='joined-string'),
            call('git.upstart', '/etc/init/nova-api-os-compute.conf',
                 nova_api_os_compute_context, perms=0o644,
                 templates_dir='joined-string'),
            call('git.upstart', '/etc/init/nova-cells.conf',
                 nova_cells_context, perms=0o644,
                 templates_dir='joined-string'),
            call('git.upstart', '/etc/init/nova-cert.conf',
                 nova_cert_context, perms=0o644,
                 templates_dir='joined-string'),
            call('git.upstart', '/etc/init/nova-conductor.conf',
                 nova_conductor_context, perms=0o644,
                 templates_dir='joined-string'),
            call('git.upstart', '/etc/init/nova-consoleauth.conf',
                 nova_consoleauth_context, perms=0o644,
                 templates_dir='joined-string'),
            call('git.upstart', '/etc/init/nova-console.conf',
                 nova_console_context, perms=0o644,
                 templates_dir='joined-string'),
            call('git.upstart', '/etc/init/nova-novncproxy.conf',
                 nova_novncproxy_context, perms=0o644,
                 templates_dir='joined-string'),
            call('git.upstart', '/etc/init/nova-objectstore.conf',
                 nova_objectstore_context, perms=0o644,
                 templates_dir='joined-string'),
            call('git.upstart', '/etc/init/nova-scheduler.conf',
                 nova_scheduler_context, perms=0o644,
                 templates_dir='joined-string'),
            call('git.upstart', '/etc/init/nova-spiceproxy.conf',
                 nova_spiceproxy_context, perms=0o644,
                 templates_dir='joined-string'),
            call('git.upstart', '/etc/init/nova-xvpvncproxy.conf',
                 nova_xvpvncproxy_context, perms=0o644,
                 templates_dir='joined-string'),
        ]
        self.assertEquals(self.render.call_args_list, expected)
        self.assertTrue(self.apt_update.called)
        self.apt_install.assert_called_with(['novnc', 'spice-html5',
                                             'websockify'], fatal=True)

    @patch('os.listdir')
    @patch('os.path.join')
    @patch('os.path.exists')
    @patch('os.symlink')
    @patch('shutil.copytree')
    @patch('shutil.rmtree')
    def test_git_post_install_systemd(self, rmtree, copytree, symlink, exists,
                                      join, listdir):
        projects_yaml = openstack_origin_git
        join.return_value = 'joined-string'
        self.lsb_release.return_value = {'DISTRIB_RELEASE': '15.10'}
        self.git_pip_venv_dir.return_value = '/mnt/openstack-git/venv'
        utils.git_post_install(projects_yaml)
        expected = [
            call('git/nova_sudoers', '/etc/sudoers.d/nova_sudoers',
                 {}, perms=288),
            call('git/nova-api-os-compute.init.in.template',
                 'joined-string', {'daemon_path': 'joined-string'},
                 perms=420),
            call('git/nova-baremetal.init.in.template',
                 'joined-string', {'daemon_path': 'joined-string'},
                 perms=420),
            call('git/nova-cells.init.in.template',
                 'joined-string', {'daemon_path': 'joined-string'},
                 perms=420),
            call('git/nova-cert.init.in.template',
                 'joined-string', {'daemon_path': 'joined-string'},
                 perms=420),
            call('git/nova-conductor.init.in.template',
                 'joined-string', {'daemon_path': 'joined-string'},
                 perms=420),
            call('git/nova-consoleauth.init.in.template',
                 'joined-string', {'daemon_path': 'joined-string'},
                 perms=420),
            call('git/nova-console.init.in.template',
                 'joined-string', {'daemon_path': 'joined-string'},
                 perms=420),
            call('git/nova-novncproxy.init.in.template',
                 'joined-string', {'daemon_path': 'joined-string'},
                 perms=420),
            call('git/nova-scheduler.init.in.template',
                 'joined-string', {'daemon_path': 'joined-string'},
                 perms=420),
            call('git/nova-serialproxy.init.in.template',
                 'joined-string', {'daemon_path': 'joined-string'},
                 perms=420),
            call('git/nova-spiceproxy.init.in.template',
                 'joined-string', {'daemon_path': 'joined-string'},
                 perms=420),
            call('git/nova-xvpvncproxy.init.in.template',
                 'joined-string', {'daemon_path': 'joined-string'},
                 perms=420),
        ]
        self.assertEquals(self.render.call_args_list, expected)

    def _test_is_api_ready(self, tgt):
        fake_config = MagicMock()
        with patch.object(utils, 'incomplete_relation_data') as ird:
            ird.return_value = (not tgt)
            self.assertEqual(utils.is_api_ready(fake_config), tgt)
            ird.assert_called_with(
                fake_config, utils.REQUIRED_INTERFACES)

    def test_is_api_ready_true(self):
        self._test_is_api_ready(True)

    def test_is_api_ready_false(self):
        self._test_is_api_ready(False)

    def test_assess_status(self):
        with patch.object(utils, 'assess_status_func') as asf:
            callee = MagicMock()
            asf.return_value = callee
            utils.assess_status('test-config')
            asf.assert_called_once_with('test-config')
            callee.assert_called_once_with()
            self.os_application_version_set.assert_called_with(
                utils.VERSION_PACKAGE
            )

    @patch.object(utils, 'get_optional_interfaces')
    @patch.object(utils, 'check_optional_relations')
    @patch.object(utils, 'REQUIRED_INTERFACES')
    @patch.object(utils, 'services')
    @patch.object(utils, 'determine_ports')
    @patch.object(utils, 'make_assess_status_func')
    def test_assess_status_func(self,
                                make_assess_status_func,
                                determine_ports,
                                services,
                                REQUIRED_INTERFACES,
                                check_optional_relations,
                                get_optional_interfaces):
        services.return_value = 's1'
        REQUIRED_INTERFACES.copy.return_value = {'int': ['test 1']}
        get_optional_interfaces.return_value = {'opt': ['test 2']}
        determine_ports.return_value = 'p1'
        utils.assess_status_func('test-config')
        # ports=None whilst port checks are disabled.
        make_assess_status_func.assert_called_once_with(
            'test-config',
            {'int': ['test 1'], 'opt': ['test 2']},
            charm_func=check_optional_relations, services='s1',
            ports=None)

    def test_pause_unit_helper(self):
        with patch.object(utils, '_pause_resume_helper') as prh:
            utils.pause_unit_helper('random-config')
            prh.assert_called_once_with(utils.pause_unit, 'random-config')
        with patch.object(utils, '_pause_resume_helper') as prh:
            utils.resume_unit_helper('random-config')
            prh.assert_called_once_with(utils.resume_unit, 'random-config')

    @patch.object(utils, 'services')
    @patch.object(utils, 'determine_ports')
    def test_pause_resume_helper(self, determine_ports, services):
        f = MagicMock()
        services.return_value = 's1'
        determine_ports.return_value = 'p1'
        with patch.object(utils, 'assess_status_func') as asf:
            asf.return_value = 'assessor'
            utils._pause_resume_helper(f, 'some-config')
            asf.assert_called_once_with('some-config')
            # ports=None whilst port checks are disabled.
            f.assert_called_once_with('assessor', services='s1', ports=None)

    @patch.object(utils, 'service_pause')
    @patch.object(utils, 'service_resume')
    @patch.object(utils, 'config')
    @patch.object(utils, 'filter_installed_packages')
    def test_disable_aws_compat_services_uinstalled(self,
                                                    filter_installed_packages,
                                                    config, service_resume,
                                                    service_pause):
        filter_installed_packages.return_value = utils.AWS_COMPAT_SERVICES
        utils.update_aws_compat_services()
        config.assert_not_called()
        service_pause.assert_not_called()
        service_resume.assert_not_called()

    @patch.object(utils, 'service_pause')
    @patch.object(utils, 'service_resume')
    @patch.object(utils, 'config')
    @patch.object(utils, 'filter_installed_packages')
    def test_disable_aws_compat_services_true(self, filter_installed_packages,
                                              config, s_resume, s_pause):
        filter_installed_packages.return_value = []
        config.return_value = True
        utils.update_aws_compat_services()

        s_resume.assert_not_called()
        s_pause.assert_has_calls([call(s) for s in utils.AWS_COMPAT_SERVICES])

    @patch.object(utils, 'service_pause')
    @patch.object(utils, 'service_resume')
    @patch.object(utils, 'config')
    @patch.object(utils, 'filter_installed_packages')
    def test_disable_aws_compat_services_false(self, filter_installed_packages,
                                               config, s_resume, s_pause):
        filter_installed_packages.return_value = []
        config.return_value = False
        utils.update_aws_compat_services()

        s_resume.assert_has_calls([call(s) for s in utils.AWS_COMPAT_SERVICES])
        s_pause.assert_not_called()
