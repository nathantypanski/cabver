# cabver.py

Quick script to make parsing the output of [cabal](https://www.haskell.org/cabal/) and [ghc-pkg](https://www.haskell.org/haskellwiki/Ghc-pkg) a bit easier.

## Why

Because `ghc-pkg` does a poor job of formatting its output for use in scripts. I usually have two questions when I first query my GHC package database:

1. What are my duplicate packages?
2. Which packages have new upstream releases?

I didn't have a good way to answer this. Now I do.

## Usage

To show installed packages:

```
$ ./cabver.py -i
Cabal 1.18.1.3 1.20.0.3
Decimal 0.4.1
HTTP 4000.2.17 4000.2.19
JuicyPixels 3.1.7.1
...
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

Passing `--multiple` or `-m` will list only packages for which a newer version is currently installed:

```
$ ./cabver.py -m -i
Cabal: 1.18.1.3 1.20.0.3
HTTP: 4000.2.17 4000.2.19
network: 2.4.2.3 2.6.0.2
texmath: 0.6.6.3 0.8
zip-archive: 0.2.3.2 0.2.3.4
```

This may be combined with the other switches as needed:

```
$ ./cabver.py -m -i zip-archive Cabal
Cabal: 1.18.1.3 1.20.0.3
zip-archive: 0.2.3.2 0.2.3.4
```

Providing the `--id` argument gives nice IDs for use with `ghc-pkg` or `cabal-install`:

```
$ ./cabver.py -m -i --id
Cabal-1.18.1.3
Cabal-1.20.0.3
HTTP-4000.2.17
HTTP-4000.2.19
network-2.4.2.3
network-2.6.0.2
texmath-0.6.6.3
texmath-0.8
zip-archive-0.2.3.2
zip-archive-0.2.3.4
```

To check for updates to all packages, use `--new-versions` (`-n`):

```
$ ./cabver.py -n | head -n 5
Decimal: 0.4.1 -> 0.4.2
JuicyPixels: 3.1.7.1 -> 3.2
aeson: 0.7.0.6 -> 0.8.0.2
aeson-pretty: 0.7.1 -> 0.7.2
asn1-encoding: 0.8.1.3 -> 0.9.0
```

When run with `--id`, `-n` will list the IDs of the new versions:

```
$ ./cabver.py -n --id | head -n 5
Decimal-0.4.2
JuicyPixels-3.2
aeson-0.8.0.2
aeson-pretty-0.7.2
asn1-encoding-0.9.0
```

Which you can then pass into `cabal install` using `xargs`, if you so desire:

```
./cabver.py -n --id | head -n 2 | xargs cabal install
Resolving dependencies...
Configuring Decimal-0.4.2...
^C
```
