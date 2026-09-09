#!/usr/bin/env python3


def base_build_does_not_wait_for_ui_publication(times):
    return times['base', 'build', 'start'] < times['ui', 'publish', 'end']
