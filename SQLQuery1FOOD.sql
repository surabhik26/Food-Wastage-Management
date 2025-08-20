
SELECT COUNT(*) FROM Providers;
SELECT COUNT(*) FROM Receivers;
SELECT COUNT(*) FROM Food;
SELECT COUNT(*) FROM Claims;

-- Peek at the first few rows
SELECT TOP 5 * FROM Providers;
SELECT TOP 5 * FROM Receivers;
SELECT TOP 5 * FROM Food;
SELECT TOP 5 * FROM Claims;

--How many food providers and receivers are there in each city?
SELECT 
    ISNULL(p.City, r.City) AS City,
    COUNT(DISTINCT p.Provider_ID) AS Total_Providers,
    COUNT(DISTINCT r.Receiver_ID) AS Total_Receivers
FROM Providers p
FULL OUTER JOIN Receivers r 
    ON p.City = r.City
GROUP BY ISNULL(p.City, r.City)
ORDER BY City;

--Which type of food provider contributes the most food?
SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
FROM Food
GROUP BY Provider_Type
ORDER BY Total_Quantity DESC;

--What is the contact information of food providers in a specific city?
SELECT Name, Contact, City
FROM Providers
WHERE City LIKE '%New%';-- change city

--Which receivers have claimed the most food?
SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims
FROM Claims c
JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.Name
ORDER BY Total_Claims DESC;

--What is the total quantity of food available from all providers?
SELECT SUM(Quantity) AS Total_Available_Food
FROM Food;

--Which city has the highest number of food listings?
SELECT Location, COUNT(Food_ID) AS Total_Listings
FROM Food
GROUP BY Location
ORDER BY Total_Listings DESC;

--What are the most commonly available food types?
SELECT Food_Type, COUNT(*) AS Count
FROM Food
GROUP BY Food_Type
ORDER BY Count DESC;

--How many food claims have been made for each food item?
SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
FROM Claims c
JOIN Food f ON c.Food_ID = f.Food_ID
GROUP BY f.Food_Name
ORDER BY Total_Claims DESC;

--Which provider has had the highest number of successful food claims?
SELECT p.Name, COUNT(c.Claim_ID) AS Successful_Claims
FROM Claims c
JOIN Food f ON c.Food_ID = f.Food_ID
JOIN Providers p ON f.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Name
ORDER BY Successful_Claims DESC;

--What percentage of food claims are completed vs. pending vs. cancelled?
SELECT Status,
       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Claims) AS Percentage
FROM Claims
GROUP BY Status;

--What is the average quantity of food claimed per receiver?
SELECT r.Name, AVG(f.Quantity) AS Avg_Quantity_Claimed
FROM Claims c
JOIN Food f ON c.Food_ID = f.Food_ID
JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.Name;

--Which meal type is claimed the most?
SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
FROM Claims c
JOIN Food f ON c.Food_ID = f.Food_ID
GROUP BY f.Meal_Type
ORDER BY Total_Claims DESC;

--What is the total quantity of food donated by each provider?
SELECT p.Name, SUM(f.Quantity) AS Total_Donated
FROM Providers p
JOIN Food f ON p.Provider_ID = f.Provider_ID
GROUP BY p.Name
ORDER BY Total_Donated DESC;

--Top 5 cities with the most claims (demand hotspots).
SELECT r.City, COUNT(c.Claim_ID) AS Total_Claims
FROM Claims c
JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.City
ORDER BY Total_Claims DESC
OFFSET 0 ROWS FETCH NEXT 5 ROWS ONLY;

--Trends in food wastage (expired but unclaimed food).
SELECT COUNT(*) AS Expired_Unclaimed
FROM Food f
LEFT JOIN Claims c ON f.Food_ID = c.Food_ID
WHERE f.Expiry_Date < GETDATE() AND c.Claim_ID IS NULL;

ALTER TABLE Providers
DROP COLUMN Provider_ID;

ALTER TABLE Providers
ADD Provider_ID INT IDENTITY(1,1) PRIMARY KEY;