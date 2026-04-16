# Cloudinary Setup Guide for Ekiane E-commerce

## 1. Create Cloudinary Account
1. Go to [cloudinary.com](https://cloudinary.com)
2. Sign up for a free account
3. Verify your email

## 2. Get Your Credentials
After logging in:
1. Go to Dashboard
2. Note down your:
   - Cloud Name
   - API Key
   - API Secret

## 3. Set Environment Variables in Render
In your Render dashboard:
1. Go to your service settings
2. Add these environment variables:
   ```
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```
   Or use the combined format:
   ```
   CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
   ```

## 4. Deploy and Test
1. Deploy your updated code to Render
2. Test image uploads in your admin panel
3. Images will now be stored on Cloudinary and served via CDN

## Benefits
- ✅ Persistent storage (survives Render restarts)
- ✅ Fast global CDN delivery
- ✅ Automatic image optimization
- ✅ Free tier: 25GB storage, 25GB monthly bandwidth
- ✅ Pay-as-you-go pricing beyond free tier

## Cost Estimate
- Free tier covers most small e-commerce sites
- ~$10-20/month for moderate usage
- Scales automatically with your traffic