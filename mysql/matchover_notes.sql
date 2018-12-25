SELECT * FROM amsterdamteam9.`match`
WHERE MatchDate >= '2018-12-01' AND MatchOver is Null
ORDER BY MatchDate Desc, StartTime Asc;