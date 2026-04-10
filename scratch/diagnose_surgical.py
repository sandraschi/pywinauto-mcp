from pywinauto import Application


def surgical_diagnose():
    print("Surgical Diagnosis of Paint UI...")
    try:
        app = Application(backend="uia").connect(path="mspaint.exe")
        win = app.window(class_name="MSPaintApp")
        win.set_focus()
        print(f"Connected to Paint: {win.texts()}")

        # Search for buttons and list items related to colors and brushes
        print("\nScanning for colors and brushes...")
        descendants = win.descendants()

        keywords = ["Green", "Blue", "Red", "Sky", "Meadow", "Brush", "Oil", "Water", "color"]
        matches = []
        for d in descendants:
            name = d.window_text()
            aid = d.automation_id()
            ctype = d.control_type()

            if any(k.lower() in name.lower() or k.lower() in aid.lower() for k in keywords):
                matches.append(f"[{ctype}] Name='{name}', AutoID='{aid}'")

        for m in sorted(list(set(matches))):
            print(f"MATCH: {m}")

        # Test mouse movement definitely
        import pyautogui

        print("\nTesting mouse movement (Visible Square)...")
        w, h = pyautogui.size()
        cx, cy = w // 2, h // 2
        pyautogui.moveTo(cx - 100, cy - 100, duration=1)
        pyautogui.moveTo(cx + 100, cy - 100, duration=1)
        pyautogui.moveTo(cx + 100, cy + 100, duration=1)
        pyautogui.moveTo(cx - 100, cy + 100, duration=1)
        pyautogui.moveTo(cx - 100, cy - 100, duration=1)
        print("Mouse test complete.")

    except Exception as e:
        print(f"Surgical error: {e}")


if __name__ == "__main__":
    surgical_diagnose()
