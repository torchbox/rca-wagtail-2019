import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import ProgrammeTeaser from './ProgrammeTeaser';

const ProgrammesResults = ({ programmes }) => {
    const nbResults = `${programmes.length} results match your search`;
    return (
        <div className="bg bg--dark section section--end">
            <div className="programmes-results">
                <p>{nbResults}</p>
                {programmes.length === 0 ? (
                    <>
                        <br />
                        <br />
                        <br />
                        <br />
                        <br />
                        <br />
                        <br />
                        <br />
                        <br />
                        <br />
                    </>
                ) : null}
                <>
                    {programmes.map((prog) => {
                        return (
                            <ProgrammeTeaser key={prog.id} programme={prog} />
                        );
                    })}
                </>
            </div>
        </div>
    );
};

ProgrammesResults.propTypes = {
    programmes: PropTypes.arrayOf().isRequired,
};

ProgrammesResults.defaultProps = {};

const mapStateToProps = ({ programmes }) => {
    return {
        programmes: programmes.results,
    };
};

export default connect(mapStateToProps)(ProgrammesResults);
