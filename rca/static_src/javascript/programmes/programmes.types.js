import PropTypes from 'prop-types';

/**
 * A Programme page’s serialised attributes, coming from the Wagtail API.
 * Please make sure this stays up-to-date with APIField and serializers.
 */
export const programmePage = {
    id: PropTypes.number.isRequired,
    meta: PropTypes.shape({
        type: PropTypes.string.isRequired,
        detail_url: PropTypes.string.isRequired,
        html_url: PropTypes.string.isRequired,
        slug: PropTypes.string.isRequired,
        first_published_at: PropTypes.string.isRequired,
    }).isRequired,
    title: PropTypes.string.isRequired,
    degree_level: PropTypes.shape({
        id: PropTypes.number.isRequired,
        title: PropTypes.string.isRequired,
    }).isRequired,
    programme_description_subtitle: PropTypes.string.isRequired,
    pathway_blocks: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.string.isRequired,
            type: PropTypes.string.isRequired,
            value: PropTypes.shape({
                heading: PropTypes.string.isRequired,
                preview_text: PropTypes.string.isRequired,
                body: PropTypes.string.isRequired,
                link: PropTypes.shape({
                    title: PropTypes.string.isRequired,
                    url: PropTypes.string.isRequired,
                }).isRequired,
            }).isRequired,
        }),
    ).isRequired,
    hero_image_square: PropTypes.shape({
        url: PropTypes.string.isRequired,
        width: PropTypes.number.isRequired,
        height: PropTypes.number.isRequired,
    }).isRequired,
};

export const programmePageShape = PropTypes.shape(programmePage);

export const programmeCategoryItem = {
    id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
    title: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
};

export const programmeCategoryItemShape = PropTypes.shape(
    programmeCategoryItem,
);

export const programmeCategory = {
    id: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    items: PropTypes.arrayOf(programmeCategoryItemShape).isRequired,
};

export const programmeCategoryShape = PropTypes.shape(programmeCategory);

export const programmeCategories = PropTypes.arrayOf(programmeCategoryShape);
