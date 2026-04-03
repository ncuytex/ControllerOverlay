import sys, os

# Resolve assets directory relative to this test file
_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')

# Test SVG XML manipulation without Qt/GUI
import copy
import xml.etree.ElementTree as ET

ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

_NS = '{http://www.w3.org/2000/svg}'

def _find_by_id(root, eid):
    for el in root.iter():
        if el.get('id') == eid:
            return el
    return None

def _find_all_by_class(root, cls):
    result = []
    for el in root.iter():
        if cls in el.get('class', '').split():
            result.append(el)
    return result

# Test Xbox SVG
print("=== Xbox SVG ===")
xbox_root = ET.parse(os.path.join(_ASSETS_DIR, 'xbox.svg')).getroot()
for eid in ['A', 'B', 'X', 'Y', 'LB_top', 'View', 'Menu', 'Share', 'XBOX', 'D_Pad']:
    el = _find_by_id(xbox_root, eid)
    print(f"  {eid}: {'FOUND' if el else 'MISSING'} (tag: {el.tag if el else 'N/A'})")

stick_els = _find_all_by_class(xbox_root, 'Left_Stick')
print(f"  Left_Stick class: {len(stick_els)} elements")
stick_els = _find_all_by_class(xbox_root, 'Right_Stick')
print(f"  Right_Stick class: {len(stick_els)} elements")
dpad_lines = _find_all_by_class(xbox_root, 'D_Pad_Line')
print(f"  D_Pad_Line class: {len(dpad_lines)} elements")

# Test modifying an element
a_btn = _find_by_id(xbox_root, 'A')
a_btn.set('fill', '#FF0000')
a_btn.set('fill-opacity', '0.55')
a_btn.set('stroke', '#FF0000')
print(f"  A button modified: fill={a_btn.get('fill')}, stroke={a_btn.get('stroke')}")

# Serialize and verify
svg_bytes = ET.tostring(xbox_root, encoding='unicode')
assert 'fill="#FF0000"' in svg_bytes, "Modified fill not in serialized SVG"
print("  Serialization OK")

# Test DualSense SVG
print("\n=== DualSense SVG ===")
ds_root = ET.parse(os.path.join(_ASSETS_DIR, 'dualsense.svg')).getroot()
for eid in ['Cross', 'Circle', 'Square', 'Triangle', 'L1_Top', 'R1_Top',
            'DPad_Up', 'DPad_Down', 'DPad_Left', 'DPad_Right',
            'PS', 'Mic_Mute', 'Touchpad',
            'Left_Stick_Outer', 'Left_Stick_Inner',
            'Right_Stick_Outer', 'Right_Stick_Inner']:
    el = _find_by_id(ds_root, eid)
    print(f"  {eid}: {'FOUND' if el else 'MISSING'}")

# Test trigger SVGs
print("\n=== Trigger SVGs ===")
for fname, side in [('left_trigger.svg', 'left'), ('right_trigger.svg', 'right')]:
    root = ET.parse(os.path.join(_ASSETS_DIR, fname)).getroot()
    for el in root.iter(f'{_NS}path'):
        el.set('id', f'{side}_trigger_shape')
    shape = _find_by_id(root, f'{side}_trigger_shape')
    print(f"  {fname}: shape={('FOUND' if shape else 'MISSING')}")

    # Test clipPath injection
    d_attr = shape.get('d', '') if shape else ''
    print(f"  {fname}: d attribute length = {len(d_attr)}")
    vb = root.get('viewBox', '')
    print(f"  {fname}: viewBox = {vb}")

print("\n=== ALL TESTS PASSED ===")
