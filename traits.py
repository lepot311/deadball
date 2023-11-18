from enums import Traits

from events import Event


class TODOEvent(Event):
    def resolve(self):
        pass


trait_events = {
    Traits['C+']  : TODOEvent,
    Traits['C-']  : TODOEvent,
    Traits['CN+'] : TODOEvent,
    Traits['CN-'] : TODOEvent,
    Traits['CND-']: TODOEvent,
    Traits['D+']  : TODOEvent,
    Traits['D-']  : TODOEvent,
    Traits['GB+'] : TODOEvent,
    Traits['K+']  : TODOEvent,
    Traits['P+']  : TODOEvent,
    Traits['P++'] : TODOEvent,
    Traits['P-']  : TODOEvent,
    Traits['P--'] : TODOEvent,
    Traits['S+']  : TODOEvent,
    Traits['S-']  : TODOEvent,
    Traits['ST+'] : TODOEvent,
    Traits['T+']  : TODOEvent,
}
