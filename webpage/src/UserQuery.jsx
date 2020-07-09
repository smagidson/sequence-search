import React from "react";
import PropTypes from 'prop-types';

const UserQuery = ({ searchedSequence, created, status, result, id, deleteUserQuery }) => {
    const statusClass = `status-${status}`;
    
    return (
        <div className="user-query" id={id}>
            <div className="user-query-field col-1">{searchedSequence}</div>
            <div className="user-query-field col-2"><span className={statusClass}>{status}</span></div>
            <div className="user-query-field col-3">{created}</div>
            <div className="user-query-field col-4">{result ? result : ""}</div>
            <div className="user-query-field"><button onClick={async () => await deleteUserQuery(id)}>Delete</button></div>
        </div>
    );
}

UserQuery.propTypes = {
    searchedSequence: PropTypes.string,
    status: PropTypes.string,
    result: PropTypes.string,
    id: PropTypes.string,
    deleteUserQuery: PropTypes.func
};  

export default UserQuery;