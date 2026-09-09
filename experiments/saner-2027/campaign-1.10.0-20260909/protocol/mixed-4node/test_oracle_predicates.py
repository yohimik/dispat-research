#!/usr/bin/env python3
from oracle_predicates import base_build_does_not_wait_for_ui_publication


completed_before_publication = {
    ('base', 'build', 'start'): 100,
    ('base', 'build', 'end'): 200,
    ('ui', 'publish', 'start'): 300,
    ('ui', 'publish', 'end'): 400,
}
started_after_publication = {
    ('ui', 'publish', 'start'): 100,
    ('ui', 'publish', 'end'): 200,
    ('base', 'build', 'start'): 300,
    ('base', 'build', 'end'): 400,
}

assert base_build_does_not_wait_for_ui_publication(completed_before_publication)
assert not base_build_does_not_wait_for_ui_publication(started_after_publication)
print('PASS: corrected base/UI publication predicate accepts completed-before-start and rejects waiting')
