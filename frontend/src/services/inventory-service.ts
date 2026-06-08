import { apiClient } from "./api-client";
import {
  Envelope,
  Inventory,
  InventoryDetails,
  InventoryMovement,
  StockAdjustmentPayload,
} from "../types";

export const inventoryService = {
  /** GET /api/v1/inventories — all inventories joined with product/variant metadata (ADMIN + WAREHOUSE) */
  async listAllInventories(): Promise<Envelope<InventoryDetails[]>> {
    const response = await apiClient.get<Envelope<InventoryDetails[]>>("/api/v1/inventories");
    return response.data;
  },

  /** GET /api/v1/inventories/{sku} — single inventory record by SKU */
  async getInventoryBySku(sku: string): Promise<Envelope<Inventory>> {
    const response = await apiClient.get<Envelope<Inventory>>(`/api/v1/inventories/${sku}`);
    return response.data;
  },

  /** GET /api/v1/inventories/{sku}/history — movement history for a SKU */
  async getInventoryHistory(sku: string): Promise<Envelope<InventoryMovement[]>> {
    const response = await apiClient.get<Envelope<InventoryMovement[]>>(
      `/api/v1/inventories/${sku}/history`
    );
    return response.data;
  },

  /** PATCH /api/v1/inventories/{sku}/adjust — adjust stock levels (ADMIN only) */
  async adjustStock(
    sku: string,
    payload: StockAdjustmentPayload
  ): Promise<Envelope<Inventory>> {
    const response = await apiClient.patch<Envelope<Inventory>>(
      `/api/v1/inventories/${sku}/adjust`,
      payload
    );
    return response.data;
  },

  /** GET /api/v1/inventories/alerts/low-stock — low stock alerts */
  async getLowStockAlerts(): Promise<Envelope<Inventory[]>> {
    const response = await apiClient.get<Envelope<Inventory[]>>(
      "/api/v1/inventories/alerts/low-stock"
    );
    return response.data;
  },

  /** Returns the URL for streaming CSV export (ADMIN only) */
  getExportCsvUrl(): string {
    const base =
      process.env.NEXT_PUBLIC_API_URL ||
      (typeof window !== "undefined" ? window.location.origin : "");
    return `${base}/api/v1/inventories/export/csv`;
  },
};

export default inventoryService;
