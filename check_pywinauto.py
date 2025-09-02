import pywinauto
print(f"pywinauto version: {pywinauto.__version__}")

from pywinauto import base_wrapper
print("Available in base_wrapper:")
available = [x for x in dir(base_wrapper) if not x.startswith('_')]
for item in available:
    if 'Exception' in item or 'Error' in item or 'Invalid' in item or 'Handle' in item or 'Visible' in item:
        print(f"  - {item}")

# Check if InvalidWindowHandle exists elsewhere
try:
    from pywinauto.base_wrapper import InvalidWindowHandle
    print("InvalidWindowHandle found in base_wrapper")
except ImportError as e:
    print(f"InvalidWindowHandle NOT found in base_wrapper: {e}")
    
    # Check other modules
    try:
        from pywinauto import InvalidWindowHandle
        print("InvalidWindowHandle found in main pywinauto module")
    except ImportError:
        try:
            from pywinauto.application import InvalidWindowHandle
            print("InvalidWindowHandle found in application module")
        except ImportError:
            try:
                from pywinauto.findwindows import InvalidWindowHandle
                print("InvalidWindowHandle found in findwindows module")
            except ImportError:
                try:
                    from pywinauto.win32_wrapper import InvalidWindowHandle
                    print("InvalidWindowHandle found in win32_wrapper module")
                except ImportError:
                    print("InvalidWindowHandle not found anywhere - may be deprecated")

# Also check ElementNotVisible
try:
    from pywinauto.base_wrapper import ElementNotVisible
    print("ElementNotVisible found in base_wrapper")
except ImportError:
    print("ElementNotVisible NOT found in base_wrapper")
