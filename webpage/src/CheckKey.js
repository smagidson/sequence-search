import rp from "request-promise";
import { constants } from "./constants"

export default async function evaluateKey(key) {
    const checkKey = await rp.post({
        uri: `${constants.APP_BASE_URL}/checkkey`,
        json: {
            key
        }
    });

    return checkKey.isCorrectKey;
}