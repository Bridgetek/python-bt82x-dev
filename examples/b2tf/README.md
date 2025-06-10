# Python BT82x Development Advanced Seven Segment Example

[Back](../README.md)

## Advanced Seven Segment Example

The `b2tf.py` and `b2tf2.py` examples demonstrate drawing a multiple seven segment displays on the same screen. The `b2tf.py` code uses the `sevensegment.py` widget from the [common](../common) directory to perform the drawing. The `b2tf2.py` performs the same task but uses the `ext-sevenseg` extension to draw the seven segment displays.

### Extension

In the `b2tf2.py` program the `ext-sevenseg` extension is loaded with the `extplotmemsevenseg` code. This loads extension coprocessor commands including the `CMD_SEVENSEG` function into the device. To verify the version of the extension loaded and the components the function the loader code for the `extplotmemsevenseg` returns a string containing information on the extension code. This is printed on the console when the extension is loaded:

```
print(extplotmemsevenseg.loadpatch(eve))
```
The return message is as follows:
```
plot6;plot-0.3;mem-0.1;7seg-0.1;
```
The name of the extension code is "plot6", it contains the ext-plotgraph extension version "0.3", the ext-memory extension "0.1", and the ext-sevenseg extension "0.1".

![Seven Segment Example](docs/b2tf.png)

### Running the Example

The format of the command call is as follows:

_MPSSE example:_
```
python b2tf.py --connector ft232h 
```

_FT4222 example in single mode (--mode 0):_

```
python b2tf.py --connector ft4222module 

```

_FT4222 example in dual mode (--mode 1) or quad mode (--mode 2):_

```
python b2tf.py --connector ft4222module 

```

## Files and Folders

The example contains a single file which comprises all the demo functionality.

| File/Folder | Description |
| --- | --- |
| [b2tf.py](b2tf.py) | Example source code file using the sevensegment widget |
| [b2tf2.py](b2tf.py) | Example source code file using the  function |
| [docs](docs) | Documentation support files |
