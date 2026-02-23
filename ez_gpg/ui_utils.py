# vim:ff=unix ts=4 sw=4 expandtab

import os
import shutil
import subprocess
import sys
import traceback

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class _FileChooser:
    """Cross-platform native file chooser using osascript (macOS) or
    zenity/kdialog (Linux).  Returns paths as Python lists or None."""

    @staticmethod
    def _run(script):
        """Run an AppleScript via osascript and return stdout, or None on cancel."""
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                return None
            output = result.stdout.strip()
            return output if output else None
        except Exception as e:
            print(f"osascript error: {e}")
            return None

    @staticmethod
    def _run_linux(args):
        """Run a Linux dialog tool and return stdout, or None on cancel."""
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                return None
            output = result.stdout.strip()
            return output if output else None
        except Exception as e:
            print(f"File dialog error: {e}")
            return None

    @staticmethod
    def open_file(title="Open...", multiple=False):
        if sys.platform == 'darwin':
            multi = ' with multiple selections allowed' if multiple else ''
            script = (
                f'set chosenFiles to choose file with prompt "{title}"{multi}\n'
            )
            if multiple:
                script += (
                    'set output to ""\n'
                    'repeat with f in chosenFiles\n'
                    '    set output to output & POSIX path of f & linefeed\n'
                    'end repeat\n'
                    'output'
                )
            else:
                script += 'POSIX path of chosenFiles'

            raw = _FileChooser._run(script)
            if not raw:
                return None
            paths = [p for p in raw.split('\n') if p.strip()]
            return paths if paths else None
        else:
            zenity = shutil.which('zenity')
            kdialog = shutil.which('kdialog')
            if zenity:
                args = ['zenity', '--file-selection', f'--title={title}']
                if multiple:
                    args.append('--multiple')
                    args.append('--separator=\n')
                raw = _FileChooser._run_linux(args)
                if not raw:
                    return None
                return [p for p in raw.split('\n') if p.strip()] or None
            elif kdialog:
                args = ['kdialog', '--getopenfilename', os.path.expanduser('~'), '*']
                if multiple:
                    args = ['kdialog', '--getopenfilename', os.path.expanduser('~'), '*',
                            '--multiple', '--separate-output']
                raw = _FileChooser._run_linux(args)
                if not raw:
                    return None
                return [p for p in raw.split('\n') if p.strip()] or None

        print("No native file dialog available")
        return None

    @staticmethod
    def save_file(title="Save...", default_name=""):
        if sys.platform == 'darwin':
            default_clause = ''
            if default_name:
                default_clause = f' default name "{default_name}"'
            script = (
                f'set chosenFile to choose file name with prompt "{title}"{default_clause}\n'
                'POSIX path of chosenFile'
            )
            raw = _FileChooser._run(script)
            if not raw:
                return None
            return [raw.strip()]
        else:
            zenity = shutil.which('zenity')
            kdialog = shutil.which('kdialog')
            if zenity:
                args = ['zenity', '--file-selection', '--save',
                        f'--title={title}', '--confirm-overwrite']
                if default_name:
                    args.append(f'--filename={default_name}')
                raw = _FileChooser._run_linux(args)
                if not raw:
                    return None
                return [raw.strip()]
            elif kdialog:
                path = os.path.join(os.path.expanduser('~'), default_name)
                args = ['kdialog', '--getsavefilename', path]
                raw = _FileChooser._run_linux(args)
                if not raw:
                    return None
                return [raw.strip()]

        print("No native file dialog available")
        return None


class UiUtils:
    @staticmethod
    def show_unimplemented_message_box(parent=None):
        UiUtils.show_dialog(parent,
                            "This functionality is not yet implemented!",
                            "Not Implemented")

    @staticmethod
    def show_dialog(parent, message, title="EzGpG", message_type="warning"):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=message,
            halign='center',
            valign='middle',
            color=(0, 0, 0, 1),
            text_size=(350, None),
            size_hint_y=None,
            height=120))

        btn = Button(text='OK', size_hint_y=None, height=44)
        content.add_widget(btn)

        popup = Popup(title=title, content=content,
                      size_hint=(None, None), size=(420, 250),
                      auto_dismiss=False)
        btn.bind(on_release=popup.dismiss)
        popup.open()

    @staticmethod
    def confirm_dialog(parent, message, callback=None):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=message,
            halign='center',
            valign='middle',
            color=(0, 0, 0, 1),
            text_size=(380, None),
            size_hint_y=None,
            height=140))

        btn_layout = BoxLayout(size_hint_y=None, height=44, spacing=10)
        yes_btn = Button(text='Yes')
        no_btn = Button(text='No')
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="EzGPG", content=content,
                      size_hint=(None, None), size=(450, 280),
                      auto_dismiss=False)

        def on_yes(instance):
            popup.dismiss()
            if callback:
                callback(True)

        def on_no(instance):
            popup.dismiss()
            if callback:
                callback(False)

        yes_btn.bind(on_release=on_yes)
        no_btn.bind(on_release=on_no)
        popup.open()

    @staticmethod
    def get_filename(parent=None, title="Open..."):
        selection = _FileChooser.open_file(title=title)
        if selection:
            return selection[0]
        return None

    @staticmethod
    def get_filenames(parent=None, title="Open...", multiple=True):
        return _FileChooser.open_file(title=title, multiple=multiple)

    @staticmethod
    def get_save_filename(parent, filename, title="Save..."):
        armor = True
        selection = _FileChooser.save_file(title=title, default_name=filename)
        if selection:
            chosen = selection[0]
            if chosen.endswith('.gpg'):
                armor = False
            elif not (chosen.endswith('.asc') or chosen.endswith('.gpg')):
                chosen += '.asc'
            print(f"Filename chosen as: {chosen}")
            return chosen, armor
        return None, armor

    @staticmethod
    def get_string_from_user(parent, message, title="Input required",
                             max_length=None, callback=None):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=message,
            halign='center',
            valign='middle',
            color=(0, 0, 0, 1),
            text_size=(380, None),
            size_hint_y=None,
            height=60))

        text_input = TextInput(multiline=False, size_hint_y=None, height=40)
        content.add_widget(text_input)

        btn_layout = BoxLayout(size_hint_y=None, height=44, spacing=10)
        ok_btn = Button(text='OK')
        cancel_btn = Button(text='Cancel')
        btn_layout.add_widget(ok_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(title=title, content=content,
                      size_hint=(None, None), size=(450, 260),
                      auto_dismiss=False)

        def on_ok(instance):
            text = text_input.text.strip()
            popup.dismiss()
            if callback:
                callback(text if text else None)

        def on_cancel(instance):
            popup.dismiss()
            if callback:
                callback(None)

        ok_btn.bind(on_release=on_ok)
        cancel_btn.bind(on_release=on_cancel)
        popup.open()


class error_wrapper:
    """Error handler decorator"""
    def __init__(self, func):
        self.func = func

    def _show_error(self, error, stack_trace):
        # Print details on console
        traceback.print_exception(*stack_trace)

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=f"Type: {error.__class__.__name__}\nDescription: {error}",
            halign='center',
            valign='middle',
            color=(0, 0, 0, 1),
            text_size=(400, None),
            size_hint_y=None,
            height=120))

        btn = Button(text='Close', size_hint_y=None, height=44)
        content.add_widget(btn)

        popup = Popup(title="Unhandled Error", content=content,
                      size_hint=(None, None), size=(480, 280),
                      auto_dismiss=False)
        btn.bind(on_release=popup.dismiss)
        popup.open()

    def __call__(self, *args, **kargs):
        try:
            return self.func(*args, **kargs)
        except Exception as error:
            exc_info = sys.exc_info()
            self._show_error(error, exc_info)
