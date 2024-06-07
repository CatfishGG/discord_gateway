use reqwest::Client;
use serde::{Deserialize, Serialize};
use tokio::task;
use rand::seq::SliceRandom;
use std::error::Error;

const TOKEN: &str = "MTI0MTAyMjc4Njk1NzIxNzgzNA.GPu68v.-sWyjcGdnx0UujZDZzJHXcOd0kyB1ihQzAJJJE";
const GUILD_ID: &str = "1235116653432274954";
const MESSAGE_CONTENT: &str = "This is a test message from the webhook.";
const WEBHOOK_NAME: &str = "TestWebhook";

#[derive(Serialize, Deserialize, Debug)]
struct Channel {
    id: String,
    #[serde(rename = "type")]
    channel_type: u8,
}

#[derive(Serialize, Deserialize, Debug)]
struct Webhook {
    id: String,
    token: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let client = Client::new();

    // Fetch all channels in the guild
    let channels = fetch_channels(&client, GUILD_ID).await?;
    let text_channels: Vec<Channel> = channels.into_iter().filter(|ch| ch.channel_type == 0).collect();

    if text_channels.len() < 10 {
        println!("Not enough text channels to create 10 webhooks.");
        return Ok(());
    }

    // Select 10 random text channels
    let mut rng = rand::thread_rng();
    let selected_channels: Vec<&Channel> = text_channels.choose_multiple(&mut rng, 10).collect();

    // Create 10 webhooks in the selected channels
    let mut webhooks = Vec::new();
    for (i, channel) in selected_channels.iter().enumerate() {
        if let Some(webhook) = create_webhook(&client, &channel.id, &format!("{}{}", WEBHOOK_NAME, i + 1)).await? {
            webhooks.push(webhook);
        }
    }

    if webhooks.len() < 10 {
        println!("Failed to create 10 webhooks.");
        return Ok(());
    }

    // Send 10 messages from each webhook
    let mut tasks = Vec::new();
    for webhook in webhooks {
        for _ in 0..10 {
            let client = client.clone();
            let url = format!("https://discord.com/api/webhooks/{}/{}", webhook.id, webhook.token);
            tasks.push(task::spawn(async move {
                execute_webhook(&client, &url, MESSAGE_CONTENT).await.unwrap();
            }));
        }
    }

    // Wait for all tasks to complete
    for task in tasks {
        task.await?;
    }

    Ok(())
}

async fn fetch_channels(client: &Client, guild_id: &str) -> Result<Vec<Channel>, reqwest::Error> {
    let url = format!("https://discord.com/api/v10/guilds/{}/channels", guild_id);
    let response = client
        .get(&url)
        .header("Authorization", format!("Bot {}", TOKEN))
        .send()
        .await?;
    response.json().await
}

async fn create_webhook(client: &Client, channel_id: &str, name: &str) -> Result<Option<Webhook>, reqwest::Error> {
    let url = format!("https://discord.com/api/v10/channels/{}/webhooks", channel_id);
    let response = client
        .post(&url)
        .header("Authorization", format!("Bot {}", TOKEN))
        .json(&serde_json::json!({ "name": name }))
        .send()
        .await?;

    if response.status().is_success() {
        let webhook = response.json().await?;
        Ok(Some(webhook))
    } else {
        println!("Failed to create webhook in channel {}. Status code: {}", channel_id, response.status());
        Ok(None)
    }
}

async fn execute_webhook(client: &Client, webhook_url: &str, content: &str) -> Result<(), reqwest::Error> {
    let response = client
        .post(webhook_url)
        .json(&serde_json::json!({ "content": content }))
        .send()
        .await?;

    if response.status().is_success() {
        println!("Message sent via webhook.");
    } else {
        println!("Failed to send message via webhook. Status code: {}", response.status());
    }
    Ok(())
}
