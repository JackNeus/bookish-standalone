#!/bin/sh
LC_ALL=C export LC_ALL
# tr A-Z a-z <$1 |
cat $1 |
sed 's/[]`.,;:!?"()]/ /g' |
sed 's/[^a-zA-Z0-9]/ /g' |
awk '{ gsub(/[]`.,;:!?"()\r]/, ""); for (i = 1; i <= NF; i++) print $i}' > $1".clean"
