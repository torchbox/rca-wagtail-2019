const getParams = () => new URLSearchParams(window.location.search);
const getURL = (params) => {
    const hasParams = params.keys().length > 0;
    return `${window.location.pathname}${hasParams ? '?' : ''}${params}`;
};

export const getIndexURL = () => {
    const params = getParams();
    params.delete('search');
    params.delete('category');
    params.delete('value');
    return getURL(params);
};

export const getCategoryURL = (category) => {
    const params = getParams();
    params.delete('search');
    params.set('category', category);
    params.delete('value');
    return getURL(params);
};

export const getCategoryItemURL = (category, item) => {
    const params = getParams();
    params.delete('search');
    params.set('category', category);
    params.set('value', item);
    return getURL(params);
};

export const getSearchURL = (search) => {
    const params = getParams();
    params.delete('category');
    params.delete('value');
    params.set('search', search);
    return getURL(params);
};

export const pushState = (href, e = null) => {
    if (e) {
        e.preventDefault();
    }
    window.history.pushState(null, null, href);
};
