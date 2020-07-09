import React, { useState } from "react";
import PropTypes from 'prop-types';
import rp from "request-promise";
import UserQuery from "./UserQuery";
import { constants } from "./constants";

const UserQueriesTable = ({ user, initUserQueries, getUserQueries, appkey }) => {
    const newSearch = async () => {
        if (validateSequence(newSearchSequence)) {
            const newQuery = await rp.post({
                uri: `${constants.APP_BASE_URL}/searchsequences`,
                json: {
                    user,
                    searchedSequence: newSearchSequence,
                    key: appkey
                }
            });
            // ideally there would be error-handling here. Not going to worry about it.
            setUserQueries([...userQueries, newQuery]);
        };
        setNewSearchSequence("");
    };

    const deleteUserQuery = async id => {
        const idParam = encodeURIComponent(id);
        await rp.delete({
            uri: `${constants.APP_BASE_URL}/searchsequences/${idParam}`,
            json: {
                key: appkey
            }
        });

        const removeIndex = userQueries.findIndex(q => q.id === id);
        userQueries.splice(removeIndex, 1);
        setUserQueries([...userQueries]);  // Need to supply a copy of userQueries to get this to update
    }

    const validateSequence = (sequence) => {
        const validChars = ["c", "g", "a", "t"];
        for (const c of sequence) {
            if (!validChars.includes(c.toLowerCase())) {
                alert(`${c} is an invalid DNA sequence character`);
                return false;
            }
        }
        return true;
    };

    const reload = async () => {
        const newQueries = await getUserQueries(user);
        setUserQueries(newQueries);
    }

    const [newSearchSequence, setNewSearchSequence] = useState("");
    const [userQueries, setUserQueries] = useState(initUserQueries);
    
    return (
        <div className="user-queries-table">
            <div className="user-query">
                <div className="col-1 table-header">Searched Sequence</div>
                <div className="col-2 table-header">Search Status</div>
                <div className="col-3 table-header">Started</div>
                <div className="col-4 table-header">Result</div>
            </div>
            {userQueries.map((userQuery, i) => (
                <UserQuery
                    searchedSequence={userQuery.searchedSequence}
                    status={userQuery.status}
                    created={userQuery.created}
                    result={userQuery.result}
                    id={userQuery.id}
                    deleteUserQuery={deleteUserQuery}
                    key={userQuery.id}
                />
            ))}
            <div className="new-search">
                <div className="new-search-text">
                    <textarea
                        placeholder="Sequence"
                        value={newSearchSequence}
                        className="new-search-textarea"
                        onChange={evt => setNewSearchSequence(evt.target.value)}>
                    </textarea>
                </div>
                <div className="new-search-button">
                    <button onClick={async () => await newSearch()}>New search</button>
                </div>
            </div>
            <div><button onClick={() => reload()}>Reload</button></div>
        </div>
    );
}

UserQueriesTable.propTypes = {
    user: PropTypes.string,
    initUserQueries: PropTypes.array,
    getUserQueries: PropTypes.func,
    appkey: PropTypes.string
};  

export default UserQueriesTable;