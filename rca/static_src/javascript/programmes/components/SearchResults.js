import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

const SearchResults = ({ programmes }) => {
    const nbResults = `${programmes.length} results match your search`;
    return (
        <div>
            <p>{nbResults}</p>
            {programmes.map((prog) => {
                return <div key={prog.id}>{prog.title}</div>;
            })}
        </div>
    );
};

SearchResults.propTypes = {
    programmes: PropTypes.arrayOf().isRequired,
};

SearchResults.defaultProps = {};

const mapStateToProps = ({ programmes }) => {
    return {
        programmes: programmes.results,
    };
};

export default connect(mapStateToProps)(SearchResults);
