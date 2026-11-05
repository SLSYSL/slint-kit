# SPDX-License-Identifier: GPL-3.0-or-later
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

import capture_pipeline as pipeline


def png(width, height):
    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data
                + struct.pack('>I', zlib.crc32(kind + data)))
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress((b'\0' + b'\xff' * width * 4) * height))
            + chunk(b'IEND', b''))


class CatalogueCaptureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.docs = Path(temporary.name)
        (self.docs / 'content').mkdir()
        self.path = self.docs / 'content/captures.json'
        self.path.write_text(json.dumps({'components': {}}))
        self.patch = patch.object(pipeline, 'DOCS', self.docs)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def capture(self, locale):
        source = self.docs / 'examples' / ('fr' if locale == 'fr' else '') / 'chip-button.slint'
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text('localized fixture: ' + locale)
        stem = 'chip-button' + ('-fr' if locale == 'fr' else '')
        outputs = [self.docs / (stem + '@2x.png'), self.docs / (stem + '.png')]
        outputs[0].write_bytes(png(4, 2))
        outputs[1].write_bytes(png(2, 1))
        pipeline.update_legacy({'kind': pipeline.SceneKind.CATALOGUE, 'slug': 'chip-button',
                                'locale': locale, 'suffix': '', 'outputs': outputs,
                                'recipe': {'theme': 'light', 'textScale': 1}},
                               {'origin': {'capturedAt': '2026-11-04T20:00:00Z'}})
        return source, outputs

    def test_runtime_recipe_keeps_locale_theme_scale_and_viewport_out_of_the_binary_route(self):
        task = {'id': 'catalogue:button:fr:dark:2', 'kind': pipeline.SceneKind.CATALOGUE,
                'slug': 'button', 'sceneKey': 'scene', 'key': 'render',
                'outputs': [pipeline.ROOT / 'example.png'],
                'recipe': {'locale': 'fr', 'theme': 'dark', 'textScale': 2, 'viewport': [1000, 1000]}}
        scene = pipeline.browser_scene(task, {'base': '/shared-bundle'})
        self.assertEqual(scene['recipe'], task['recipe'])
        self.assertEqual(scene['kind'], 'catalogue')
        self.assertEqual(scene['base'], '/shared-bundle')

    def test_light_and_dark_starter_proofs_do_not_overwrite_each_other(self):
        capture_file = self.docs / 'content/starter-captures.json'
        capture_file.write_text('{}')
        source = self.docs / 'quickstart/button'
        source.mkdir(parents=True)
        (source / 'main.rs').write_text('host')
        for theme in ('dark', 'light', 'dark'):
            suffix = '-dark' if theme == 'dark' else ''
            image = source / f'preview{suffix}@2x.png'
            image.write_bytes(png(4, 2))
            task = {'kind': pipeline.SceneKind.STARTER, 'slug': 'button', 'key': theme,
                    'outputs': [image], 'recipe': {'theme': theme}}
            with patch('starter_sources.source_directory', return_value=source), \
                 patch('starter_sources.source_files', return_value=['main.rs']):
                pipeline.update_legacy(task, {'origin': {'environment': {'platform': 'test'}}})
        proof = json.loads(capture_file.read_text())['button']
        self.assertEqual(proof['theme'], 'light')
        self.assertEqual(proof['image']['file'], 'preview@2x.png')
        self.assertEqual(proof['dark']['theme'], 'dark')
        self.assertEqual(proof['dark']['image']['file'], 'preview-dark@2x.png')

    def test_new_component_registers_both_locales_in_either_order(self):
        for order in [('en', 'fr'), ('fr', 'en')]:
            with self.subTest(order=order):
                self.path.write_text(json.dumps({'components': {}}))
                for locale in order:
                    self.capture(locale)
                component = json.loads(self.path.read_text())['components']['chip-button']
                for locale, entry in [('en', component), ('fr', component['locales']['fr'])]:
                    source = self.docs / 'examples' / ('fr' if locale == 'fr' else '') / 'chip-button.slint'
                    self.assertEqual(entry['exampleSha256'], pipeline.digest(source.read_bytes()))
                    self.assertEqual((entry['width'], entry['height']), (2, 1))
                    self.assertEqual([variant['pixelDensity'] for variant in entry['variants']], [2, 1])

    def test_recapture_replaces_variants_and_preserves_other_locale(self):
        self.capture('en')
        self.capture('fr')
        before = json.loads(self.path.read_text())['components']['chip-button']['locales']['fr']
        self.capture('en')
        component = json.loads(self.path.read_text())['components']['chip-button']
        self.assertEqual(component['locales']['fr'], before)
        self.assertEqual(len(component['variants']), 2)

    def test_existing_component_can_gain_its_first_french_capture(self):
        self.path.write_text(json.dumps({'components': {'chip-button': {'variants': [], 'width': 99}}}))
        self.capture('fr')
        component = json.loads(self.path.read_text())['components']['chip-button']
        self.assertEqual(component['width'], 99)
        self.assertEqual(len(component['locales']['fr']['variants']), 2)


if __name__ == '__main__':
    unittest.main()
