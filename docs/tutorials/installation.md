!!! warning
    The project is in alpha stage and not ready for any use. This tutorial does not work yet, and it is included so it can be later updated.

In this tutorial, we will install Kamihi using `uv` and verify that it works correctly.

## Python package

Kamihi is published as a Python package on [PyPI](https://example.com). We can install it using any package manager that supports Python packages, such as `pip`, `poetry`, or `uv`. We recommend using `uv` for its speed and simplicity.

=== "uv"

    <!-- termynal -->
    ``` sh
    > uv add kamihi
    ---> 100%
    Installed 1 package in XXms
    + kamihi==X.X.X
    ```

=== "pip"
    <!-- termynal -->
    ``` sh
    > pip install kamihi
    Collecting kamihi
    Downloading kamihi-X.X.X-py3-none-any.whl (XX kB)
    ---> 100%
    Installing collected packages: kamihi
    Successfully installed kamihi-X.X.X
    ```

=== "poetry"
    <!-- termynal -->
    ``` sh
    > poetry add kamihi
    Using version X.X.X for kamihi

    Updating dependencies
    Resolving dependencies... (0.0s)

    Writing lock file

    Package operations: 1 install, 0 updates, 0 removals

      - Installing kamihi (X.X.X)
    
    ---> 100%

    Successfully installed kamihi-X.X.X
    ```

## Verification

Now let's verify our installation by running the following command:

```sh
$ python -c "from kamihi import __version__; print(__version__)"

X.X.X
```

## Next steps

You've successfully installed Kamihi and verified it's working! Now, we can create our first project. Check out
the [quick start guide](quick-start.md) to get started.
