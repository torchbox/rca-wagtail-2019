const getParams = () => new URLSearchParams(window.location.search);
const getURL = (params) => {
    const queryString = params.toString();
    const hasQuery = queryString !== '';
    return `${window.location.pathname}${hasQuery ? '?' : ''}${queryString}`;
};

export const getIndexURL = () => {
    const params = getParams();
    params.delete('search');
    params.delete('category');
    params.delete('value');
    params.delete('part-time');
    return getURL(params);
};

export const getCategoryURL = (category, activeLength) => {
    const params = getParams();
    params.delete('search');
    params.set('category', category);
    params.delete('value');
    if (activeLength === 'true') {
        params.set('part-time', 'true');
    } else {
        params.delete('part-time');
    }
    return getURL(params);
};

export const getCategoryItemURL = (category, item, slug, activeLength) => {
    const params = getParams();
    params.delete('search');
    params.set('category', category);
    params.set('value', `${item}-${slug}`);
    if (activeLength === 'true') {
        params.set('part-time', 'true');
    } else {
        params.delete('part-time');
    }
    return getURL(params);
};

export const getSearchURL = (search) => {
    const params = getParams();
    params.delete('category');
    params.delete('value');
    params.delete('part-time');
    params.set('search', search);
    return getURL(params);
};

export const getCourseLengthURL = (isPartTime) => {
    const params = getParams();
    params.delete('search');
    if (isPartTime === 'true') {
        params.set('part-time', 'true');
    } else {
        params.delete('part-time');
    }
    return getURL(params);
};

export const pushState = (href, e = null) => {
    if (e) {
        e.preventDefault();
    }
    window.history.pushState(null, null, href);
};

export const replaceState = (href, e = null) => {
    if (e) {
        e.preventDefault();
    }
    window.history.replaceState(null, null, href);
};
