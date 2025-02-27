import { useState, useEffect } from 'react';
import { Paper, Divider, TextField, Button, Typography, List, ListItem, IconButton } from "@mui/material";
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';
import 'core-js/actual/array/group';

export default function SearchPanel({ user }) {
    // user is a userid string
    const [friends, setFriends] = useState([]);
    const [idValidity, setValid] = useState(true);
    const [newFriendID, setNewFriendID] = useState('');
    const [sharedCourses, setSharedCourses] = useState([]);

    const setup = async () => {
        const friendsResponse = await axios.get('/friends', { params: { userId: user } });
        setFriends(friendsResponse.data);

        const sharedClasses = await axios.get('/sharedClasses', { params: { userId: user } });
        setSharedCourses(sharedClasses.data.group(e => `${e.csub} ${e.cnum} (${e.ctype}-${e.secnum})`));
    };

    useEffect(() => {
        setup();
    }, []);

    const changeId = (event) => {
        setValid(true);
        setNewFriendID(event.target.value);
    }

    // Once userId is stored, add case for user adding themself
    const addFriend = async () => {
        console.log(newFriendID);
        if (!newFriendID || newFriendID.length !== 8) {
            setValid('Invalid ID');
            return;
        }
        const response = await axios.post('/modifyFriends', {
            userId: user,
            target: newFriendID
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        setup();
    }

    const removeFriend = async (id) => {
        console.log(id)

        const response = await axios.delete('/modifyFriends', {
            params: {
                userId: user,
                target: id
            }
        });
        setup();
    }

    return (
        <Paper style={{ margin: '0 4em', padding: '1em', display: 'flex' }}>
            <div style={{ width: '400px' }}>
                <div style={{ marginBottom: '1em' }}>My Friends</div>
                <div style={{ display: 'flex', justifyContent: 'space-around' }}>
                    <TextField
                        id="standard-basic" label="User ID" variant="standard"
                        value={newFriendID}
                        style={{ width: '100px' }}
                        error={idValidity !== true}
                        onChange={changeId}
                    />
                    <Button
                        variant="contained" onClick={addFriend}>
                        Add
                    </Button>
                </div>

                <Typography variant="caption" color="red" style={{ minHeight: '1em' }}>
                    {idValidity !== true ? idValidity : "ㅤ"}
                </Typography>

                <List style={{ marginTop: '1em' }}>
                    {
                        friends.map((element, idx) =>
                            <ListItem
                                key={idx}
                                secondaryAction={
                                    <IconButton onClick={() => removeFriend(element.id)} edge="end" aria-label="delete">
                                        <DeleteIcon></DeleteIcon>
                                    </IconButton>
                                }>
                                {`${element.first_name} ${element.last_name} (${element.id})`}</ListItem>
                        )
                    }
                </List>
            </div>
            <Divider orientation="vertical" flexItem></Divider>
            <div style={{ flexBasis: '100%' }}>
                Shared Courses
                {
                    sharedCourses.length === 0
                        ?
                        <Typography variant="caption">
                            <div style={{ margin: '2em 0' }}>You do not have any courses in common with any of your friends</div>
                        </Typography>
                        :
                        <List>
                            {
                                Object.keys(sharedCourses).map(cid => {
                                    const course = sharedCourses[cid];
                                    const classmates = course
                                        .map(e => `${e.first_name} ${e.last_name}`)
                                        .join(', ');

                                    return (
                                        <>
                                            <ListItem key={cid} dense>
                                                {cid + ': '}
                                            </ListItem>
                                            <ListItem style={{ marginBottom: '1em' }} dense key={cid + 'classmates'}>
                                                <div>taken with {classmates}</div>
                                            </ListItem>
                                        </>
                                    );
                                })
                            }
                        </List>
                }
            </div>
        </Paper>
    )
}