
Generala:
	echo "#!/bin/bash" > Generala
	echo "python3 test_generala.py \"\$$@\"" >> Generala
	chmod u+x Generala