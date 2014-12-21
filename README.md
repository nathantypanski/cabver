# cabver.py

Quick script to make parsing the output of [cabal](https://www.haskell.org/cabal/) and [ghc-pkg](https://www.haskell.org/haskellwiki/Ghc-pkg) a bit easier.

## Usage

To show installed packages:

```
$ ./cabver.py -i
Cabal 1.18.1.3 1.20.0.3
Decimal 0.4.1
HTTP 4000.2.17 4000.2.19
JuicyPixels 3.1.7.1
List 0.5.1
QuickCheck 2.7.6
SHA 1.6.4.1
X11 1.6.1.2
aeson 0.7.0.6
aeson-pretty 0.7.1
array 0.5.0.0
asn1-encoding 0.8.1.3
...
warp 3.0.0.8
x509 1.4.12
x509-store 1.4.4
x509-system 1.4.5
x509-validation 1.5.0
xhtml 3000.2.1
xml 1.3.13
yaml 0.8.8.4
zip-archive 0.2.3.2 0.2.3.4
zlib 0.5.4.1
```

You can also display just a specific package:

```
./cabver.py -i pandoc
pandoc 1.13.1
```

Or a list of them:

```
./cabver.py -i pandoc unix
pandoc 1.13.1
unix 2.7.0.1
```

Passing `--old` will list only "old" packages, i.e., packages for which a newer version is currently registered.

```
./cabver.py -i --old
Cabal 1.18.1.3
HTTP 4000.2.17
network 2.4.2.3
texmath 0.6.6.3
zip-archive 0.2.3.2
```

This may be combined with the other switches as needed:

```
$ ./cabver.py -i zip-archive Cabal --old
Cabal 1.18.1.3
zip-archive 0.2.3.2
```

Providing the `--id` argument gives nice IDs for use with `ghc-pkg` or `cabal-install`:

```
$ ./cabver.py -i zip-archive Cabal --old --id
Cabal-1.18.1.3
zip-archive-0.2.3.2
```
