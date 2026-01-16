import { apiClient } from "./client";
import { MoreInfoResponse } from "../types/moreinfo";


export const moreInfoApi = {
    // Get more info by ID
    getMoreInfoById: async (contact_id: number): Promise<MoreInfoResponse> => {
        const params: Record<string, string> = {};
        return apiClient.get<MoreInfoResponse>(`/api/contact/moreinfo/${contact_id}`, params);
    },
};