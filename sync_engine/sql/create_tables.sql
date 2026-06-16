-- ============================================================
-- BIERSYMPHONYDB - Phase 2 Schema
-- New Tables: Purchase, PurchaseItem, MenuItemConsumption
-- ============================================================


-- ============================================================
-- TABLE: Purchase
-- Purpose: Purchase order header
-- ============================================================

IF NOT EXISTS (
    SELECT * FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_NAME = 'Purchase'
)
BEGIN
    CREATE TABLE dbo.Purchase (
        PurchaseId      BIGINT IDENTITY(1,1) PRIMARY KEY,
        SupplierName    NVARCHAR(200) NOT NULL,
        InvoiceNumber   NVARCHAR(100) NOT NULL,
        PurchaseDate    DATETIME NOT NULL DEFAULT GETDATE(),
        TotalAmount     DECIMAL(18,2) NOT NULL DEFAULT 0,
        CreatedAt       DATETIME NOT NULL DEFAULT GETDATE()
    );

    PRINT 'Created table: Purchase';
END
ELSE
    PRINT 'Table already exists: Purchase';


-- ============================================================
-- TABLE: PurchaseItem
-- Purpose: Purchase line items
-- ============================================================

IF NOT EXISTS (
    SELECT * FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_NAME = 'PurchaseItem'
)
BEGIN
    CREATE TABLE dbo.PurchaseItem (
        PurchaseItemId  BIGINT IDENTITY(1,1) PRIMARY KEY,
        PurchaseId      BIGINT NOT NULL
            REFERENCES dbo.Purchase(PurchaseId),
        InventoryItemId INT NOT NULL
            REFERENCES dbo.InventoryItem(InventoryItemId),
        Quantity        DECIMAL(18,4) NOT NULL,
        UnitPrice       DECIMAL(18,2) NOT NULL,
        TotalPrice      DECIMAL(18,2) NOT NULL
    );

    PRINT 'Created table: PurchaseItem';
END
ELSE
    PRINT 'Table already exists: PurchaseItem';


-- ============================================================
-- TABLE: MenuItemConsumption
-- Purpose: Maps POS menu items to inventory consumption
-- ============================================================

IF NOT EXISTS (
    SELECT * FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_NAME = 'MenuItemConsumption'
)
BEGIN
    CREATE TABLE dbo.MenuItemConsumption (
        Id              INT IDENTITY(1,1) PRIMARY KEY,
        MenuItemName    NVARCHAR(200) NOT NULL,
        InventoryItemId INT NOT NULL
            REFERENCES dbo.InventoryItem(InventoryItemId),
        ConsumptionPerQty DECIMAL(18,4) NOT NULL
    );

    PRINT 'Created table: MenuItemConsumption';
END
ELSE
    PRINT 'Table already exists: MenuItemConsumption';
