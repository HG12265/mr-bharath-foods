import { apiClient } from "./api-client";
import { Envelope, Inventory } from "../types";

export interface StockAdjustmentPayload {
  warehouse_id: string;
  quantity: number; // delta
  location_code?: string;
}

export const inventoryService = {
  async getInventoryBySku(sku: string): Promise<Envelope<Inventory>> {
    const response = await apiClient.get<Envelope<Inventory>>(`/api/v1/inventories/${sku}`);
    return response.data;
  },

  async adjustStock(sku: string, payload: StockAdjustmentPayload): Promise<Envelope<Inventory>> {
    const response = await apiClient.patch<Envelope<Inventory>>(`/api/v1/inventories/${sku}/adjust`, payload);
    return response.data;
  },

  async getLowStockAlerts(): Promise<Envelope<Inventory[]>> {
    const response = await apiClient.get<Envelope<Inventory[]>>("/api/v1/inventories/alerts/low-stock");
    return response.data;
  },
};

export default inventoryService;
