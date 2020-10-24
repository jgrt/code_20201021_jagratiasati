## Body Mass Index Calculator

##### BMI (kg)/m^2 along with health risk and category of bmi, provides Command line interface to easily run program.

### Technologies Used (Top Level):
1. Python 3.8
2. Pandas
3. pytest

### Getting Started

* Clone this repo to your machine
```
$ git clone https://github.com/jgrt/code_20201021_jagratiasati.git
```

#### Manual Setup
* after cloning repo, run following commands to build and run calculator
```
$ cd code_20201021_jagratiasati
$ python3 setup.py install
$ pip install code_20201021_jagratiasati
```

#### Using Makefile
```
$ cd code_20201021_jagratiasati
$ make install
$ make test ##  to run pytest
```

#### Usage
##### Arguments:
1. -help
2. -input : Required, input file path
3. -output: Required, output file path
4. -summary: Required, summary file path
5. -config: Optional, if not passed, will use default config

* all files are in json format

```
$ calculator -input path/to/input.json -output path/to/output.json -summary path/to/summary.json -cf path/to/config.json
```




