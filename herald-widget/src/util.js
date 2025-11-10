export function parseFragment() {
    const fragmentString = globalThis.location.hash || '?';
    return new URLSearchParams(fragmentString.substring(Math.max(fragmentString.indexOf('?'), 0)));
}

export function assertParam(fragment, name) {
    const val = fragment.get(name);
    if (!val) throw new Error(`${name} is not present in URL - cannot load widget`);
    return val;
}

export function handleError(e) {
    console.error(e);
    const container = document.getElementById('container');
    if (container) {
        container.innerText = 'There was an error with the widget. See JS console for details.';
    }
}
