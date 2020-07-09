import React, { useState } from "react";
import rp from "request-promise";
import UserQueriesTable from "./UserQueriesTable";
import checkKey from "./CheckKey";
import { constants } from "./constants";

const Page = () => {
    const getUserQueries = async givenUser => {
        const userParam = encodeURIComponent(givenUser);
        const userQueriesResponse = await rp.get(`${constants.APP_BASE_URL}/searchsequences?user=${userParam}`);
        const userQueriesData = JSON.parse(userQueriesResponse).queries;
        return userQueriesData;
    }

    const saveUser = async (evt) => {
        evt.preventDefault();

        if (!(await checkKey(key))) {
            alert(`Incorrect key (${key})`);
            return;
        }

        const userQueriesData = await getUserQueries(inputtedUser);
        
        setUserQueries(userQueriesData);
        setUser(inputtedUser);
    };

    const unsetUser = () => {
        setUser(null);
        setUserQueries(null);
    }

    const [key, setKey] = useState("");
    const [inputtedUser, setInputtedUser] = useState("");
    const [user, setUser] = useState(null);
    const [userQueries, setUserQueries] = useState(null);
    
    return (
        <div>
            {!user ?
                <div className="enter-user-box">
                    <form onSubmit={async (evt) => await saveUser(evt)}>
                        <div className="text-title">Enter username:</div>
                        <div>
                            <input 
                                type="text"
                                className="login-field"
                                value={inputtedUser}
                                onChange={evt => setInputtedUser(evt.target.value)}>
                            </input>
                        </div>
                        <div className="text-title">Enter key:</div>
                        <div>
                            <input 
                                type="text"
                                className="login-field"
                                value={key}
                                onChange={evt => setKey(evt.target.value)}>
                            </input>
                        </div>
                        <input type="submit" value="Submit" className="submit-user" />
                    </form>
                </div>
                :
                <div>
                    <div className="user-title">User: {user}
                        <div className="unset-user"><button onClick={() => unsetUser()}>Change user</button></div>
                    </div>
                    <UserQueriesTable 
                        user={user}
                        initUserQueries={userQueries}
                        getUserQueries={getUserQueries}
                        appkey={key}
                    />
                </div>
            }
        </div>
    );
}

export default Page;