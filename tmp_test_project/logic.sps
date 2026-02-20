
GET DATA /TYPE=TXT /FILE='data.csv' /VARIABLES=age F3.
DO IF (age < 18).
    COMPUTE group = 0.
ELSE.
    COMPUTE group = 1.
END IF.
