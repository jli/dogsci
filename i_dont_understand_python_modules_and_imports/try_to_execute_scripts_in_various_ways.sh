#!/bin/bash

# - relative import never works when executing as script
# - relative import sometimes works when executing as module, except when PWD is same dir as code
# - absolute import is PWD sensitive, makes sense.
# - full absolute never works when executing as script
# - partial absolute sometimes works when executing as script (but this breaks using it as a lib i think)
# - executing as script only works with partial absolute imports, but this won't work with importing script as lib
#
# seems like no way to execute as a script and have the script be usable as a library
# so, either use absolute imports (with the right PWD) or relative imports, and then execute as module?



cd "$(dirname $(dirname $0))"
echo "-> 1. current directory=$PWD. executing as script."

# FAIL
echo -e "\n--> 1a. absolute import, full path."
python3 i_dont_understand_python_modules_and_imports/moduleconfusion/script_abs_import_deep.py
# works
echo -e "\n--> 1b. absolute import, partial path."
python3 i_dont_understand_python_modules_and_imports/moduleconfusion/script_abs_import_shallow.py
# FAIL
echo -e "\n--> 1c. relative import."
python3 i_dont_understand_python_modules_and_imports/moduleconfusion/script_relative_import.py


echo -e "\n\n-> 2. current directory=$PWD. executing as module (changed)."
# FAIL
echo -e "\n--> 2a. absolute import, full path."
python3 -m i_dont_understand_python_modules_and_imports.moduleconfusion.script_abs_import_deep
# FAIL
echo -e "\n--> 2b. absolute import, partial path."
python3 -m i_dont_understand_python_modules_and_imports.moduleconfusion.script_abs_import_shallow
# works
echo -e "\n--> 2c. relative import."
python3 -m i_dont_understand_python_modules_and_imports.moduleconfusion.script_relative_import




cd i_dont_understand_python_modules_and_imports
echo -e "\n\n-> 3. now current directory=$PWD (changed). executing as script (changed)."

# FAIL
echo -e "\n--> 3a. absolute import, full path."
python3 moduleconfusion/script_abs_import_deep.py
# works
echo -e "\n--> 3b. absolute import, partial path."
python3 moduleconfusion/script_abs_import_shallow.py
# FAIL
echo -e "\n--> 3c. relative import."
python3 moduleconfusion/script_relative_import.py


echo -e "\n\n-> 4. current directory=$PWD. executing as module (changed)."

# works
echo -e "\n--> 4a. absolute import, full path."
python3 -m moduleconfusion.script_abs_import_deep
# FAIL
echo -e "\n--> 4b. absolute import, partial path."
python3 -m moduleconfusion.script_abs_import_shallow
# works
echo -e "\n--> 4c. relative import."
python3 -m moduleconfusion.script_relative_import



cd moduleconfusion
echo -e "\n\n-> 5. now current directory=$PWD (changed). executing as script (changed)."

# FAIL
echo -e "\n--> 5a. absolute import, full path."
python3 script_abs_import_deep.py
# works
echo -e "\n--> 5b. absolute import, partial path."
python3 script_abs_import_shallow.py
# FAIL
echo -e "\n--> 5c. relative import."
python3 script_relative_import.py


echo -e "\n\n-> 6. current directory=$PWD. executing as module (changed)."

# FAIL
echo -e "\n--> 6a. absolute import, full path."
python3 -m script_abs_import_deep
# works
echo -e "\n--> 6b. absolute import, partial path."
python3 -m script_abs_import_shallow
# FAIL
echo -e "\n--> 6c. relative import."
python3 -m script_relative_import
