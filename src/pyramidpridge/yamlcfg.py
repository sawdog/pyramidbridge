import os
import pymlconf

# there are a couple checks in place to look for the package yml file before
# looking at what's expected to be part of the dev package.  First a check
# for PACKAGENAME_YML_PATH in the environment.
# Second /etc/pyre/package.yml and then package/etc/pyre.conf
#
YML_FILE = 'pyre.yml'
ENV_PATH = 'PYRE_YML_PATH'
YAML_PATH = '/app/'

# grab the yaml config
if os.getenv(ENV_PATH)is not None:
    yaml_path = os.getenv(ENV_PATH)
elif os.path.isfile(os.path.join(YAML_PATH, YML_FILE)):
        yaml_path = YAML_PATH
else:
    here = os.path.abspath(os.path.dirname(__file__))
    yaml_path = os.path.join(here, 'etc')

pkg_yaml = os.path.join(yaml_path, YML_FILE)

yamlcfg = pymlconf.ConfigManager()
yamlcfg.load_files(pkg_yaml)
