CREATE TABLE IF NOT EXISTS recycling_qr_pending (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    token_hash TEXT NOT NULL UNIQUE,

    fk_cd_material INTEGER NOT NULL,
    nr_weight_kilograms REAL NOT NULL,

    fk_cd_admin INTEGER NOT NULL,
    fk_cd_user_redeemed INTEGER,

    dt_created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dt_expires_at TEXT NOT NULL,
    dt_redeemed_at TEXT,

    FOREIGN KEY (fk_cd_material)
        REFERENCES materials(id),

    FOREIGN KEY (fk_cd_admin)
        REFERENCES users(id),

    FOREIGN KEY (fk_cd_user_redeemed)
        REFERENCES users(id),

    CHECK (nr_weight_kilograms > 0 AND nr_weight_kilograms <= 10)
);

CREATE INDEX IF NOT EXISTS idx_recycling_qr_pending_expiration
    ON recycling_qr_pending(dt_expires_at);
