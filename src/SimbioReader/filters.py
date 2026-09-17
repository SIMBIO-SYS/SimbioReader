#! /usr/bin/env python3


stcFilters={
    "panl":{
        "name"         : "PAN-L",
        "desc"         : "Fraction of the CCD used by the PAN-L filter",
        "id"           : "L_P700",
        "bandwidth"    : "204.3",
        "centerFilter" : "699.5",
        "interframeDel": "0.8",
        "fistLine"     : "1227",
        "firstSample"  : "576",
        "line"         : "384",
        "sample"       : "896"
    },
    "panh":{
        "name"         : "PAN-H",
        "desc"         : "Fraction of the CCD used by the PAN-H filter",
        "id"           : "H_P700",
        "bandwidth"    : "204.3",
        "centerFilter" : "699.5",
        "interframeDel": "0.8",
        "fistLine"     : "1227",
        "firstSample"  : "576",
        "line"         : "384",
        "sample"       : "896"
    },
    "f920":{
          "name"         : "F920-L",
          "desc"         : "Fraction of the CCD used by the F920-L filter",
          "id"           : "L_F920",
          "bandwidth"    : "20",
          "centerFilter" : "920",
          "interframeDel": "0.8",
          "fistLine"     : "1953",
          "firstSample"  : "576",
          "line"         : "64",
          "sample"       : "896"
    },
    "f550":{
        "name"         : "F550-L",
        "desc"         : "Fraction of the CCD used by the F550-L filter",
        "id"           : "L_F550",
        "bandwidth"    : "20",
        "centerFilter" : "550",
        "interframeDel": "0.8",
        "fistLine"     : "1745",
        "firstSample"  : "576",
        "line"         : "64",
        "sample"       : "896"
    },
    "f420":{
        "name"         : "F420-H",
        "desc"         : "Fraction of the CCD used by the F420-H filter",
        "id"           : "H_F420",
        "bandwidth"    : "20",
        "centerFilter" : "420",
        "interframeDel": "0.8",
        "fistLine"     : "240",
        "firstSample"  : "576",
        "line"         : "64",
        "sample"       : "896"
    },
    "f750":{
        "name"         : "F750-H",
        "desc"         : "Fraction of the CCD used by the F750-H filter",
        "id"           : "H_F750",
        "bandwidth"    : "20",
        "centerFilter" : "750",
        "interframeDel": "0.8",
        "fistLine"     : "32",
        "firstSample"  : "576",
        "line"         : "64",
        "sample"       : "896"
    },
     "winx":{
        "name"         : "WIN-X",
        "desc"         : "Fraction of the CCD used for calibration",
        "id"           : "Win-X",
        "bandwidth"    : "0",
        "centerFilter" : "0",
        "interframeDel": "0.8",
        "fistLine"     : "100",
        "firstSample"  : "192",
        "line"         : "64",
        "sample"       : "128"
    },
}
hricFilters={
    "fpan":{
        "name"         : "FPAN",
        "desc"         : "Portion of CMOS with panchromatic filter",
        "id"           : "FPAN",
        "bandwidth"    : "504.9",
        "centerFilter" : "652.3",
        "interframeDel": "__",
        "fistLine"     : "938",
        "firstSample"  : "0",
        "line"         : "640",
        "sample"       : "2048"
    },
    "f550":{
        "name"         : "F550",
        "desc"         : "Portion of CMOS with broadband F550 filter",
        "id"           : "F550",
        "bandwidth"    : "40.4",
        "centerFilter" : "549.3",
        "interframeDel": "__",
        "fistLine"     : "1662",
        "firstSample"  : "0",
        "line"         : "384",
        "sample"       : "2048"
    },
    "f750":{
        "name"         : "F750",
        "desc"         : "Portion of CMOS with broadband F750 filter",
        "id"           : "F750",
        "bandwidth"    : "39.9",
        "centerFilter" : "752.9",
        "interframeDel": "__",
        "fistLine"     : "2",
        "firstSample"  : "0",
        "line"         : "384",
        "sample"       : "2048"
    },
    "f880":{
        "name"         : "F880",
        "desc"         : "Portion of CMOS with broadband F750 filter",
        "id"           : "F880",
        "bandwidth"    : "39.8",
        "centerFilter" : "880.1",
        "interframeDel": "__",
        "fistLine"     : "470",
        "firstSample"  : "0",
        "line"         : "384",
        "sample"       : "2048"
    },
}
