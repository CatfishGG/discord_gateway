use hyper::body::Body;
use hyper::client::Client;
use hyper::http::Method;
use hyper::Request;
use hyper::Uri;
use serde::{Deserialize, Serialize};
use std::error::Error;
use tokio::task;
use rand::seq::SliceRandom;

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
    let text_channels: Vec<&Channel> = channels.iter().filter(|ch| ch.channel_type == 0).collect();

    if text_channels.len() < 10 {
        println!("Not enough text channels to create 10 webhooks.");
        return Ok(());
    }

    // Select 10 random text channels
    let mut rng = rand::thread_rng();
    let selected_channels: Vec<&&Channel> = text_channels.choose_multiple(&mut rng, 10).collect();

    // Create 10 webhooks in the selected channels
    let mut webhooks = Vec::new();
    for (i, &&channel) in selected_channels.iter().enumerate() {
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
            println!("Executing webhook URL: {}", url); // Debug print
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

async fn fetch_channels(client: &Client<hyper::client::HttpConnector>, guild_id: &str) -> Result<Vec<Channel>, Box<dyn Error>> {
    let url = format!("https://discord.com/api/v10/guilds/{}/channels", guild_id);
    println!("Fetching channels URL: {}", url); // Debug print
    let uri: Uri = url.parse()?;
    println!("Parsed URI: {}", uri); // Debug print
    let req = Request::builder()
        .method(Method::GET)
        .uri(uri)
        .header("Authorization", format!("Bot {}", TOKEN))
        .body(Body::empty())?;
    
    let res = client.request(req).await?;
    let body_bytes = hyper::body::to_bytes(res.into_body()).await?;
    let channels: Vec<Channel> = serde_json::from_slice(&body_bytes)?;
    Ok(channels)
}

async fn create_webhook(client: &Client<hyper::client::HttpConnector>, channel_id: &str, name: &str) -> Result<Option<Webhook>, Box<dyn Error>> {
    let url = format!("https://discord.com/api/v10/channels/{}/webhooks", channel_id);
    println!("Creating webhook URL: {}", url); // Debug print
    let uri: Uri = url.parse()?;
    println!("Parsed URI: {}", uri); // Debug print
    let json = serde_json::json!({ "name": name });
    let req = Request::builder()
        .method(Method::POST)
        .uri(uri)
        .header("Authorization", format!("Bot {}", TOKEN))
        .header("Content-Type", "application/json")
        .body(Body::from(json.to_string()))?;
    
    let res = client.request(req).await?;
    if res.status().is_success() {
        let body_bytes = hyper::body::to_bytes(res.into_body()).await?;
        let webhook: Webhook = serde_json::from_slice(&body_bytes)?;
        Ok(Some(webhook))
    } else {
        println!("Failed to create webhook in channel {}. Status code: {}", channel_id, res.status());
        Ok(None)
    }
}

async fn execute_webhook(client: &Client<hyper::client::HttpConnector>, webhook_url: &str, content: &str) -> Result<(), Box<dyn Error>> {
    let uri: Uri = webhook_url.parse()?;
    println!("Executing webhook URL: {}", uri); // Debug print
    let json = serde_json::json!({ "content": content });
    let req = Request::builder()
        .method(Method::POST)
        .uri(uri)
        .header("Content-Type", "application/json")
        .body(Body::from(json.to_string()))?;
    
    let res = client.request(req).await?;
    if res.status().is_success() {
        println!("Message sent via webhook.");
    } else {
        println!("Failed to send message via webhook. Status code: {}", res.status());
    }
    Ok(())
}
