// Contributors:
// * Contributor: <rokanas@student.chalmers.se>
import { writable } from "svelte/store";

export type UserRequest = {
    request_id: number,
    created_at: number,
    lesion_type: string,
    user: string,
};

export const userRequests = writable<UserRequest[]>([]);